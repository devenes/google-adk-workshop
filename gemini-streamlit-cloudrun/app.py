# pylint: disable=broad-exception-caught,broad-exception-raised,invalid-name
"""
This module demonstrates the usage of the Gemini API in Vertex AI within a Streamlit application.

It showcases several multimodal capabilities of Gemini models:
  - Freeform text prompting with configurable parameters
  - Story generation from structured inputs
  - Marketing campaign generation
  - Image understanding (furniture, appliances, ER diagrams, glasses, math)
  - Video understanding (description, tags, highlights, geolocation)

Deployment: Runs locally or on Google Cloud Run.
Authentication: Uses either a GOOGLE_API_KEY (Vertex AI Express Mode)
                or Application Default Credentials (ADC) with a GCP project.
"""

import os  # Standard library: read environment variables (API keys, project/region settings)

from google import genai  # Google Gen AI SDK: the main client for calling Gemini models
import google.auth  # Google Auth library: auto-detects credentials (ADC, service accounts, etc.)
from google.genai.types import GenerateContentConfig, Part, ThinkingConfig
# GenerateContentConfig: bundles generation parameters (temperature, max tokens, top_p, etc.)
# Part: wraps multimodal content (images, videos) referenced by URI
# ThinkingConfig: controls the model's internal "thinking budget" (extended reasoning tokens)
import httpx  # HTTP client: used to query the GCP metadata server for region info
import streamlit as st  # Streamlit: the web UI framework that turns this script into an app


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _project_id() -> str:
    """
    Auto-detect the active Google Cloud Project ID using Application Default Credentials (ADC).

    ADC checks for credentials in this order:
      1. GOOGLE_APPLICATION_CREDENTIALS env var (path to a service account JSON key)
      2. gcloud auth application-default login credentials
      3. Attached service account (when running on GCP: Cloud Run, GCE, etc.)

    Returns:
        str: The Google Cloud Project ID associated with the current credentials.

    Raises:
        Exception: If credentials are missing or the project cannot be determined.
    """
    try:
        # google.auth.default() returns (credentials, project_id)
        # We only need the project_id here, so credentials is assigned to _ (ignored)
        _, project = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError as e:
        raise Exception("Could not automatically determine credentials") from e
    if not project:
        raise Exception("Could not determine project from credentials.")
    return project


def _region() -> str:
    """
    Detect the Google Cloud region by querying the GCP instance metadata server.

    The metadata server is an internal HTTP endpoint available only on GCP instances
    (Cloud Run, GCE, GKE, etc.) at http://metadata.google.internal.
    The 'Metadata-Flavor: Google' header is required for security; it prevents
    accidental SSRF attacks by only responding to requests that include this header.

    If the metadata server is unreachable (e.g., running locally), falls back to 'us-central1'.

    Returns:
        str: The short region name, e.g. 'us-central1'.
    """
    try:
        resp = httpx.get(
            # GCP metadata endpoint that returns the full region path like:
            # "projects/123456789/regions/us-central1"
            "http://metadata.google.internal/computeMetadata/v1/instance/region",
            headers={"Metadata-Flavor": "Google"},  # Required header to access metadata
        )
        # The response is a path like "projects/123456789/regions/us-central1"
        # .split("/")[-1] grabs only the last segment: "us-central1"
        return resp.text.split("/")[-1]
    except Exception:
        # If not running on GCP (e.g., local dev), fall back to a sensible default region
        return "us-central1"


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

# MODELS maps model IDs (placeholder strings replaced at deploy time) to
# human-readable display names shown in the Streamlit UI radio button.
# Keys   = model IDs sent to the Gemini API
# Values = friendly names displayed to the user
MODELS = {
    "__GEMINI_FLASH_LITE_MODEL_ID__": "__GEMINI_FLASH_LITE_MODEL_NAME__",
    "__GEMINI_PRO_MODEL_ID__": "__GEMINI_PRO_MODEL_NAME__",
    "__GEMINI_FLASH_MODEL_ID__": "__GEMINI_FLASH_MODEL_NAME__",
}

# THINKING_BUDGET_MODELS is the set of model IDs that support "thinking budget"
# (extended internal reasoning before generating the final response).
# Only these models will display the thinking budget controls in the UI.
THINKING_BUDGET_MODELS = {
    "__GEMINI_PRO_MODEL_ID__",
    "__GEMINI_FLASH_MODEL_ID__",
    "__GEMINI_FLASH_LITE_MODEL_ID__",
}


# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

@st.cache_resource  # Cache this function's result: the client is created once and reused
                    # across all Streamlit reruns, avoiding repeated auth/network overhead.
def load_client() -> genai.Client:
    """
    Create and return a Google Gen AI client configured for Vertex AI.

    Auth priority:
      1. GOOGLE_API_KEY env var  →  Vertex AI Express Mode (no project/region needed)
      2. ADC + GOOGLE_CLOUD_PROJECT  →  Standard Vertex AI (requires a GCP project)

    Region priority:
      1. GOOGLE_CLOUD_REGION env var  (explicit override)
      2. GCP metadata server          (auto-detected when running on GCP)
      3. "global"                     (last-resort fallback)

    Returns:
        genai.Client: Authenticated client ready to call Gemini models.
    """
    # Read optional API key for Vertex AI Express Mode (simpler auth, no project required)
    API_KEY = os.environ.get("GOOGLE_API_KEY")

    # Read project ID: prefer explicit env var, fall back to ADC auto-detection
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", _project_id())

    # Read region: prefer explicit env var, fall back to metadata server detection
    LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", _region())

    # Validate that we have at least one valid auth method available
    if not API_KEY and not PROJECT_ID:
        st.error(
            "🚨 Configuration Error: Please set either `GOOGLE_API_KEY` or ensure "
            "Application Default Credentials (ADC) with a Project ID are configured."
        )
        st.stop()  # Halt Streamlit execution; nothing below this line will run

    if not LOCATION:
        st.warning(
            "⚠️ Could not determine Google Cloud Region. Using 'global'. "
            "Ensure GOOGLE_CLOUD_REGION environment variable is set or metadata service is accessible if needed."
        )
        LOCATION = "global"  # Fallback when region cannot be determined

    # Build and return the Gen AI client
    # vertexai=True: route requests through Vertex AI instead of the public Gemini API
    return genai.Client(
        vertexai=True,      # Use Vertex AI endpoint (requires GCP project + region OR API key)
        project=PROJECT_ID, # GCP project where Vertex AI is enabled
        location=LOCATION,  # GCP region (e.g. "us-central1")
        api_key=API_KEY,    # Optional: API key for Vertex AI Express Mode
    )


def get_model_name(name: str | None) -> str:
    """
    Resolve a model ID to its human-readable display name.

    Used as the `format_func` for the Streamlit radio button so users see
    friendly names instead of raw model IDs.

    Args:
        name: A model ID key from the MODELS dict, or None.

    Returns:
        str: The display name, or "Gemini" as a safe fallback.
    """
    if not name:
        return "Gemini"  # Safe fallback when no model is selected yet
    return MODELS.get(name, "Gemini")  # Look up display name; default to "Gemini" if unknown


# ---------------------------------------------------------------------------
# Page header & navigation buttons
# ---------------------------------------------------------------------------

# Add a button that links to the source code on GitHub
st.link_button(
    "View on GitHub",
    "https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/sample-apps/gemini-streamlit-cloudrun",
)

# K_SERVICE is an env var automatically set by Cloud Run with the service name.
# If present, we know we're running in Cloud Run and can show a deep-link button.
cloud_run_service = os.environ.get("K_SERVICE")
if cloud_run_service:
    # Show a button to open this service's page in the Cloud Run console
    st.link_button(
        "Open in Cloud Run",
        f"https://console.cloud.google.com/run/detail/us-central1/{cloud_run_service}/source",
    )

# Main page title with a rainbow divider; ":sparkles:" renders as an emoji in Streamlit
st.header(":sparkles: Gemini API in Vertex AI", divider="rainbow")

# Initialize the Gemini API client (cached — only runs once per session)
client = load_client()

# ---------------------------------------------------------------------------
# Global model selector
# ---------------------------------------------------------------------------

# Radio button to choose which Gemini model to use for ALL tabs
# - MODELS.keys() provides the list of model ID options
# - format_func=get_model_name renders friendly names in the UI
# - key="selected_model" lets Streamlit track the widget's value across reruns
selected_model = st.radio(
    "Select Model:",
    MODELS.keys(),
    format_func=get_model_name,
    key="selected_model",
    horizontal=True,  # Display options in a single horizontal row
)

# ---------------------------------------------------------------------------
# Thinking budget controls (only shown for supported models)
# ---------------------------------------------------------------------------

thinking_budget = None  # Default: no thinking budget specified (model uses its default)

if selected_model in THINKING_BUDGET_MODELS:
    # Let the user choose how to control the model's internal reasoning tokens
    thinking_budget_mode = st.selectbox(
        "Thinking budget",
        ("Auto", "Manual", "Off"),
        key="thinking_budget_mode_selectbox",
        # Auto  = model decides how many thinking tokens to use
        # Manual = user sets an explicit token limit via slider
        # Off   = disable thinking entirely (thinking_budget=0)
    )

    if thinking_budget_mode == "Manual":
        # Slider to set the maximum number of thinking tokens (0–24576)
        thinking_budget = st.slider(
            "Thinking budget token limit",
            min_value=0,
            max_value=24576,  # Maximum thinking tokens supported by the API
            step=1,
            key="thinking_budget_manual_slider",
        )
    elif thinking_budget_mode == "Off":
        thinking_budget = 0  # Explicitly disable thinking

# Build a ThinkingConfig object only when the user has specified a budget.
# If thinking_budget is None (Auto mode), we pass thinking_config=None to the API,
# which lets the model decide autonomously.
thinking_config = (
    ThinkingConfig(thinking_budget=thinking_budget)
    if thinking_budget is not None
    else None
)

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------

# Create five top-level tabs; each tab holds a different demo feature
freeform_tab, tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✍️ Freeform",           # Free-form prompting with full parameter control
        "📖 Generate Story",     # Structured story generation
        "📢 Marketing Campaign", # AI-generated marketing campaigns
        "🖼️ Image Playground",  # Multimodal image understanding demos
        "🎬 Video Playground",   # Multimodal video understanding demos
    ]
)

# ===========================================================================
# TAB: Freeform
# ===========================================================================
with freeform_tab:
    st.subheader("Enter Your Own Prompt")

    # --- Generation parameters ---
    # Temperature controls randomness/creativity:
    #   0.0 = deterministic (always picks the highest-probability token)
    #   2.0 = very random/creative
    temperature = st.slider(
        "Select the temperature (Model Randomness):",
        min_value=0.0,
        max_value=2.0,
        value=0.5,  # Default: moderate creativity
        step=0.05,
        key="temperature",
    )

    # max_output_tokens caps the length of the generated response
    max_output_tokens = st.slider(
        "Maximum Number of Tokens to Generate:",
        min_value=1,
        max_value=8192,
        value=2048,  # Default: up to 2048 tokens (~1500 words)
        step=1,
        key="max_output_tokens",
    )

    # Top-P (nucleus sampling): the model only considers the smallest set of tokens
    # whose cumulative probability is >= top_p. Lower = more focused, higher = more diverse.
    top_p = st.slider(
        "Select the Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.95,  # Default: consider top 95% of the probability mass
        step=0.05,
        key="top_p",
    )

    # Multi-line text area for the user's custom prompt
    prompt = st.text_area(
        "Enter your prompt here...",
        key="prompt",
        height=200,
    )

    # Bundle all generation parameters into a single config object
    config = GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
        thinking_config=thinking_config,  # None if Auto mode; ThinkingConfig otherwise
    )

    # "Generate" button — only triggers generation when clicked AND a prompt is provided
    generate_freeform = st.button("Generate", key="generate_freeform")
    if generate_freeform and prompt:
        with st.spinner(
            f"Generating response using {get_model_name(selected_model)} ..."
        ):
            # Two sub-tabs: one for the model's response, one to inspect the prompt/parameters
            first_tab1, first_tab2 = st.tabs(["Response", "Prompt"])
            with first_tab1:
                # Call the Gemini API: send the prompt and config, get back the text response
                response = client.models.generate_content(
                    model=selected_model,    # Model ID (e.g. gemini-2.0-flash)
                    contents=prompt,         # The user's prompt string
                    config=config,           # Temperature, tokens, top_p, thinking_config
                ).text  # .text extracts the plain-text response from the API response object

                if response:
                    st.markdown(response)  # Render response as Markdown (supports bold, lists, etc.)
            with first_tab2:
                # Show what parameters were used for this generation (useful for learning)
                st.markdown(
                    f"""Parameters:\n- Model ID: `{selected_model}`\n- Temperature: `{temperature}`\n- Top P: `{top_p}`\n- Max Output Tokens: `{max_output_tokens}`\n"""
                )
                if thinking_budget is not None:
                    st.markdown(f"- Thinking Budget: `{thinking_budget}`\n")
                st.code(prompt, language="markdown")  # Display the raw prompt in a code block

# ===========================================================================
# TAB 1: Generate Story
# ===========================================================================
with tab1:
    st.subheader("Generate a story")

    # --- Story premise inputs ---
    # Each st.text_input / st.radio / st.multiselect captures one aspect of the story
    character_name = st.text_input(
        "Enter character name: \n\n", key="character_name", value="Mittens"
    )
    character_type = st.text_input(
        "What type of character is it? \n\n", key="character_type", value="Cat"
    )
    character_persona = st.text_input(
        "What personality does the character have? \n\n",
        key="character_persona",
        value="Mittens is a very friendly cat.",
    )
    character_location = st.text_input(
        "Where does the character live? \n\n",
        key="character_location",
        value="Andromeda Galaxy",
    )
    # Multiselect: user can pick multiple genres/themes for the story
    story_premise = st.multiselect(
        "What is the story premise? (can select multiple) \n\n",
        [
            "Love",
            "Adventure",
            "Mystery",
            "Horror",
            "Comedy",
            "Sci-Fi",
            "Fantasy",
            "Thriller",
        ],
        key="story_premise",
        default=["Love", "Adventure"],  # Pre-selected options
    )
    # Map UI creativity level to a temperature value
    creative_control = st.radio(
        "Select the creativity level: \n\n",
        ["Low", "High"],
        key="creative_control",
        horizontal=True,
    )
    length_of_story = st.radio(
        "Select the length of the story: \n\n",
        ["Short", "Long"],
        key="length_of_story",
        horizontal=True,
    )

    # Translate UI selections to numeric generation parameters
    if creative_control == "Low":
        temperature = 0.30   # Low temperature = more predictable/structured prose
    else:
        temperature = 0.95   # High temperature = more creative/varied writing

    if length_of_story == "Short":
        max_output_tokens = 2048   # ~5 chapters
    else:
        max_output_tokens = 8192   # ~10 chapters (max allowed by API config here)

    # Build the prompt using an f-string that injects all user inputs
    # Providing explicit structure in the prompt guides the model to follow the format
    prompt = f"""Write a {length_of_story} story based on the following premise: \n
  character_name: {character_name} \n
  character_type: {character_type} \n
  character_persona: {character_persona} \n
  character_location: {character_location} \n
  story_premise: {",".join(story_premise)} \n
  If the story is "short", then make sure to have 5 chapters or else if it is "long" then 10 chapters.
  Important point is that each chapters should be generated based on the premise given above.
  First start by giving the book introduction, chapter introductions and then each chapter. It should also have a proper ending.
  The book should have prologue and epilogue.
  """

    # Config without top_p (not needed here; story generation uses temperature + token limit)
    config = GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        thinking_config=thinking_config,
    )

    generate_t2t = st.button("Generate my story", key="generate_t2t")
    if generate_t2t and prompt:
        with st.spinner(
            f"Generating your story using {get_model_name(selected_model)} ..."
        ):
            first_tab1, first_tab2 = st.tabs(["Story", "Prompt"])
            with first_tab1:
                response = client.models.generate_content(
                    model=selected_model,
                    contents=prompt,
                    config=config,
                ).text
                if response:
                    st.write("Your story:")
                    st.write(response)
            with first_tab2:
                # Show the parameters and the exact prompt sent to the model
                st.markdown(
                    f"""Parameters:\n- Model ID: `{selected_model}`\n- Temperature: `{temperature}`\n- Max Output Tokens: `{max_output_tokens}`\n"""
                )
                if thinking_budget is not None:
                    st.markdown(f"- Thinking Budget: `{thinking_budget}`\n")
                st.code(prompt, language="markdown")

# ===========================================================================
# TAB 2: Marketing Campaign
# ===========================================================================
with tab2:
    st.subheader("Generate your marketing campaign")

    # --- Campaign configuration inputs ---
    product_name = st.text_input(
        "What is the name of the product? \n\n", key="product_name", value="ZomZoo"
    )
    product_category = st.radio(
        "Select your product category: \n\n",
        ["Clothing", "Electronics", "Food", "Health & Beauty", "Home & Garden"],
        key="product_category",
        horizontal=True,
    )
    st.write("Select your target audience: ")
    # Age group segmentation for the campaign's target demographic
    target_audience_age = st.radio(
        "Target age: \n\n",
        ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        key="target_audience_age",
        horizontal=True,
    )
    # Geographic segmentation
    target_audience_location = st.radio(
        "Target location: \n\n",
        ["Urban", "Suburban", "Rural"],
        key="target_audience_location",
        horizontal=True,
    )
    st.write("Select your marketing campaign goal: ")
    # Multiple campaign goals can be selected simultaneously
    campaign_goal = st.multiselect(
        "Select your marketing campaign goal: \n\n",
        [
            "Increase brand awareness",
            "Generate leads",
            "Drive sales",
            "Improve brand sentiment",
        ],
        key="campaign_goal",
        default=["Increase brand awareness", "Generate leads"],
    )
    if campaign_goal is None:
        # Fallback in case multiselect returns None (shouldn't happen normally)
        campaign_goal = ["Increase brand awareness", "Generate leads"]

    brand_voice = st.radio(
        "Select your brand voice: \n\n",
        ["Formal", "Informal", "Serious", "Humorous"],
        key="brand_voice",
        horizontal=True,
    )
    estimated_budget = st.radio(
        "Select your estimated budget ($): \n\n",
        ["1,000-5,000", "5,000-10,000", "10,000-20,000", "20,000+"],
        key="estimated_budget",
        horizontal=True,
    )

    # Detailed prompt with structured marketing framework instructions.
    # The more specific the prompt, the more structured and useful the output.
    prompt = f"""Generate a marketing campaign for {product_name}, a {product_category} designed for the age group: {target_audience_age}.
  The target location is this: {target_audience_location}.
  Aim to primarily achieve {campaign_goal}.
  Emphasize the product's unique selling proposition while using a {brand_voice} tone of voice.
  Allocate the total budget of {estimated_budget}.
  With these inputs, make sure to follow following guidelines and generate the marketing campaign with proper headlines: \n
  - Briefly describe company, its values, mission, and target audience.
  - Highlight any relevant brand guidelines or messaging frameworks.
  - Provide a concise overview of the campaign's objectives and goals.
  - Briefly explain the product or service being promoted.
  - Define your ideal customer with clear demographics, psychographics, and behavioral insights.
  - Understand their needs, wants, motivations, and pain points.
  - Clearly articulate the desired outcomes for the campaign.
  - Use SMART goals (Specific, Measurable, Achievable, Relevant, and Time-bound) for clarity.
  - Define key performance indicators (KPIs) to track progress and success.
  - Specify the primary and secondary goals of the campaign.
  - Examples include brand awareness, lead generation, sales growth, or website traffic.
  - Clearly define what differentiates your product or service from competitors.
  - Emphasize the value proposition and unique benefits offered to the target audience.
  - Define the desired tone and personality of the campaign messaging.
  - Identify the specific channels you will use to reach your target audience.
  - Clearly state the desired action you want the audience to take.
  - Make it specific, compelling, and easy to understand.
  - Identify and analyze your key competitors in the market.
  - Understand their strengths and weaknesses, target audience, and marketing strategies.
  - Develop a differentiation strategy to stand out from the competition.
  - Define how you will track the success of the campaign.
  - Utilize relevant KPIs to measure performance and return on investment (ROI).
  Give proper bullet points and headlines for the marketing campaign. Do not produce any empty lines.
  Be very succinct and to the point.
  """

    # Higher temperature (0.8) for marketing copy = more creative/varied language
    config = GenerateContentConfig(
        temperature=0.8,
        max_output_tokens=8192,  # Allow long, detailed campaign output
        thinking_config=thinking_config,
    )

    generate_t2t = st.button("Generate my campaign", key="generate_campaign")
    if generate_t2t and prompt:
        second_tab1, second_tab2 = st.tabs(["Campaign", "Prompt"])
        with st.spinner(
            f"Generating your marketing campaign using {get_model_name(selected_model)} ..."
        ):
            with second_tab1:
                response = client.models.generate_content(
                    model=selected_model,
                    contents=prompt,
                    config=config,
                ).text
                if response:
                    st.write("Your marketing campaign:")
                    st.write(response)
            with second_tab2:
                st.code(prompt, language="markdown")  # Show the full prompt for inspection

# ===========================================================================
# TAB 3: Image Playground
# ===========================================================================
with tab3:
    st.subheader("Image Playground")

    # Five sub-tabs showcasing different image understanding capabilities
    furniture, oven, er_diagrams, glasses, math_reasoning = st.tabs(
        [
            "🛋️ Furniture recommendation",  # Multi-image comparison + recommendation
            "🔥 Oven Instructions",           # Reading physical appliance displays
            "📊 ER Diagrams",                 # Understanding technical diagrams
            "👓 Glasses",                     # Product comparison for different face shapes
            "🧮 Math Reasoning",              # Extracting and explaining math formulas
        ],
    )

    # -------------------------------------------------------------------
    # Sub-tab: Furniture recommendation
    # -------------------------------------------------------------------
    with furniture:
        st.markdown(
            """In this demo, you will be presented with a scene (e.g., a living room) and will use the Gemini model to perform visual understanding. You will see how Gemini can be used to recommend an item (e.g., a chair) from a list of furniture options as input. You can use Gemini to recommend a chair that would complement the given scene and will be provided with its rationale for such selections from the provided list."""
        )

        # Public GCS URIs for the room and chair images used in this demo
        room_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/retail-recommendations/rooms/living_room.jpeg"
        chair_1_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/retail-recommendations/furnitures/chair1.jpeg"
        chair_2_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/retail-recommendations/furnitures/chair2.jpeg"
        chair_3_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/retail-recommendations/furnitures/chair3.jpeg"
        chair_4_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/retail-recommendations/furnitures/chair4.jpeg"

        # Display images inline in the Streamlit app for context
        st.image(room_image_uri, width=350, caption="Image of a living room")
        st.image(
            [
                chair_1_image_uri,
                chair_2_image_uri,
                chair_3_image_uri,
                chair_4_image_uri,
            ],
            width=200,
            caption=["Chair 1", "Chair 2", "Chair 3", "Chair 4"],
        )

        st.write(
            "Our expectation: Recommend a chair that would complement the given image of a living room."
        )

        # Build a multimodal content list: interleave text labels and image Parts.
        # Part.from_uri() tells the Gemini API to fetch and process the image at the given URI.
        # mime_type tells the API what format the file is in (here: JPEG images).
        content = [
            "Consider the following chairs:",
            "chair 1:",
            Part.from_uri(file_uri=chair_1_image_uri, mime_type="image/jpeg"),
            "chair 2:",
            Part.from_uri(file_uri=chair_2_image_uri, mime_type="image/jpeg"),
            "chair 3:",
            Part.from_uri(file_uri=chair_3_image_uri, mime_type="image/jpeg"),
            "and",
            "chair 4:",
            Part.from_uri(file_uri=chair_4_image_uri, mime_type="image/jpeg"),
            "\n"
            "For each chair, explain why it would be suitable or not suitable for the following room:",
            Part.from_uri(file_uri=room_image_uri, mime_type="image/jpeg"),
            "Only recommend for the room provided and not other rooms. Provide your recommendation in a table format with chair name and reason as columns.",
        ]

        tab1, tab2 = st.tabs(["Response", "Prompt"])
        generate_image_description = st.button(
            "Generate recommendation....", key="generate_image_description"
        )
        with tab1:
            if generate_image_description and content:
                with st.spinner(
                    f"Generating recommendation using {get_model_name(selected_model)} ..."
                ):
                    # Send the multimodal content list (text + images) to Gemini
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=content,  # List of strings and Part objects (multimodal)
                        config=config,
                    ).text
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.code(content, language="markdown")  # Show the full multimodal prompt

    # -------------------------------------------------------------------
    # Sub-tab: Oven Instructions
    # -------------------------------------------------------------------
    with oven:
        stove_screen_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/stove.jpg"
        st.write(
            "Equipped with the ability to extract information from visual elements on screens, Gemini can analyze screenshots, icons, and layouts to provide a holistic understanding of the depicted scene."
        )
        st.image(stove_screen_uri, width=350, caption="Image of a oven")
        st.write(
            "Our expectation: Provide instructions for resetting the clock on this appliance in English"
        )
        # Prompt asking the model to read the image and produce actionable instructions
        prompt = """How can I reset the clock on this appliance? Provide the instructions in English.
If instructions include buttons, also explain where those buttons are physically located.
"""
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        generate_instructions_description = st.button(
            "Generate instructions", key="generate_instructions_description"
        )
        with tab1:
            if generate_instructions_description and prompt:
                with st.spinner(
                    f"Generating instructions using {get_model_name(selected_model)}..."
                ):
                    # Pass the image first, then the text question
                    # The model reads the image and answers based on what it sees
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=[
                            Part.from_uri(
                                file_uri=stove_screen_uri, mime_type="image/jpeg"
                            ),
                            prompt,  # Text question follows the image
                        ],
                    ).text
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.code(prompt, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: ER Diagrams
    # -------------------------------------------------------------------
    with er_diagrams:
        er_diag_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/er.png"
        st.write(
            "Gemini multimodal capabilities empower it to comprehend diagrams and take actionable steps, such as optimization or code generation. The following example demonstrates how Gemini can decipher an Entity Relationship (ER) diagram."
        )
        st.image(er_diag_uri, width=350, caption="Image of an ER diagram")
        st.write(
            "Our expectation: Document the entities and relationships in this ER diagram."
        )
        # Instruct the model to analyze and document the ER diagram structure
        prompt = """Document the entities and relationships in this ER diagram.
        """
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        er_diag_img_description = st.button("Generate!", key="er_diag_img_description")
        with tab1:
            if er_diag_img_description and prompt:
                with st.spinner("Generating..."):
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=[
                            Part.from_uri(file_uri=er_diag_uri, mime_type="image/jpeg"),
                            prompt,
                        ],
                    ).text
        with tab2:
            st.write("Prompt used:")
            st.code(prompt, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: Glasses
    # -------------------------------------------------------------------
    with glasses:
        compare_img_1_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/glasses1.jpg"
        compare_img_2_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/glasses2.jpg"

        st.write(
            """Gemini is capable of image comparison and providing recommendations. This can be useful in industries like e-commerce and retail.
          Below is an example of choosing which pair of glasses would be better suited to various face types:"""
        )
        # User selects their face shape to get a personalized glasses recommendation
        face_type = st.radio(
            "What is your face shape?",
            ["Oval", "Round", "Square", "Heart", "Diamond"],
            key="face_type",
            horizontal=True,
        )
        # User can choose how they want the recommendation formatted
        output_type = st.radio(
            "Select the output type",
            ["text", "table", "json"],  # Model will format its response accordingly
            key="output_type",
            horizontal=True,
        )
        st.image(
            [compare_img_1_uri, compare_img_2_uri],
            width=350,
            caption=["Glasses type 1", "Glasses type 2"],
        )
        st.write(
            f"Our expectation: Suggest which glasses type is better for the {face_type} face shape"
        )
        # Dynamic prompt injecting face shape and output format preferences
        content = [
            f"""Which of these glasses you recommend for me based on the shape of my face:{face_type}?
      I have an {face_type} shape face.
      Glasses 1: """,
            Part.from_uri(file_uri=compare_img_1_uri, mime_type="image/jpeg"),
            """
      Glasses 2: """,
            Part.from_uri(file_uri=compare_img_2_uri, mime_type="image/jpeg"),
            f"""
      Explain how you made to this decision.
      Provide your recommendation based on my face shape, and reasoning for each in {output_type} format.
      """,
        ]
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        compare_img_description = st.button(
            "Generate recommendation!", key="compare_img_description"
        )
        with tab1:
            if compare_img_description and content:
                with st.spinner(
                    f"Generating recommendations using {get_model_name(selected_model)}..."
                ):
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=[
                            Part.from_uri(file_uri=er_diag_uri, mime_type="image/jpeg"),
                            content,
                        ],
                    ).text
                    st.markdown(response)
        with tab2:
            st.write("Prompt used:")
            st.code(content, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: Math Reasoning
    # -------------------------------------------------------------------
    with math_reasoning:
        math_image_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/math_beauty.jpg"

        st.write(
            "Gemini can also recognize math formulas and equations and extract specific information from them. This capability is particularly useful for generating explanations for math problems, as shown below."
        )
        st.image(math_image_uri, width=350, caption="Image of a math equation")
        st.markdown(
            """
        Our expectation: Ask questions about the math equation as follows:
        - Extract the formula.
        - What is the symbol right before Pi? What does it mean?
        - Is this a famous formula? Does it have a name?
          """
        )
        # Structured prompt using a table format for clear, comparable answers.
        # "Surround math expressions with $" → tells the model to use LaTeX-style formatting.
        prompt = """
Follow the instructions.
Surround math expressions with $.
Use a table with a row for each instruction and its result.

INSTRUCTIONS:
- Extract the formula.
- What is the symbol right before Pi? What does it mean?
- Is this a famous formula? Does it have a name?
"""
        tab1, tab2 = st.tabs(["Response", "Prompt"])
        math_image_description = st.button(
            "Generate answers!", key="math_image_description"
        )
        with tab1:
            if math_image_description and prompt:
                with st.spinner(
                    f"Generating answers for formula using {get_model_name(selected_model)}..."
                ):
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=[
                            Part.from_uri(
                                file_uri=math_image_uri, mime_type="image/jpeg"
                            ),
                            prompt,
                        ],
                    ).text
                    st.markdown(response)
                    st.markdown("\n\n\n")  # Add vertical spacing after the response
        with tab2:
            st.write("Prompt used:")
            st.code(prompt, language="markdown")

# ===========================================================================
# TAB 4: Video Playground
# ===========================================================================
with tab4:
    st.subheader("Video Playground")

    # Four sub-tabs showcasing different video understanding capabilities
    vide_desc, video_tags, video_highlights, video_geolocation = st.tabs(
        [
            "📄 Description",    # Describe video content
            "🏷️ Tags",           # Extract relevant tags/labels from video
            "✨ Highlights",     # Extract key highlights and summarize
            "📍 Geolocation",    # Identify geographic location from visual cues
        ]
    )

    # -------------------------------------------------------------------
    # Sub-tab: Video Description
    # -------------------------------------------------------------------
    with vide_desc:
        st.markdown(
            """Gemini can also provide the description of what is going on in the video:"""
        )
        # Public GCS URI for an MP4 video of the Mediterranean Sea
        video_desc_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/mediterraneansea.mp4"

        if video_desc_uri:
            st.video(video_desc_uri)  # Embed video player directly in the Streamlit app
            st.write("Our expectation: Generate the description of the video")
            prompt = """Describe what is happening in the video and answer the following questions: \n
      - What am I looking at? \n
      - Where should I go to see it? \n
      - What are other top 5 places in the world that look like this?
      """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            vide_desc_description = st.button(
                "Generate video description", key="vide_desc_description"
            )
            with tab1:
                if vide_desc_description and prompt:
                    with st.spinner(
                        f"Generating video description using {get_model_name(selected_model)} ..."
                    ):
                        # Pass the video as a Part with mime_type="video/mp4"
                        # Gemini processes the video frames and audio (if any) to answer questions
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=[
                                Part.from_uri(
                                    file_uri=video_desc_uri, mime_type="video/mp4"
                                ),
                                prompt,
                            ],
                        ).text
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.code(prompt, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: Video Tags
    # -------------------------------------------------------------------
    with video_tags:
        st.markdown(
            """Gemini can also extract tags throughout a video, as shown below:."""
        )
        video_tags_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/photography.mp4"

        if video_tags_uri:
            st.video(video_tags_uri)
            st.write("Our expectation: Generate the tags for the video")
            # Structured Q&A prompt; asking for a table format makes output easier to read
            prompt = """Answer the following questions using the video only:
            1. What is in the video?
            2. What objects are in the video?
            3. What is the action in the video?
            4. Provide 5 best tags for this video?
            Give the answer in the table format with question and answer as columns.
      """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_tags_description = st.button(
                "Generate video tags", key="video_tags_description"
            )
            with tab1:
                if video_tags_description and prompt:
                    with st.spinner(
                        f"Generating video description using {get_model_name(selected_model)} ..."
                    ):
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=[
                                Part.from_uri(
                                    file_uri=video_tags_uri, mime_type="video/mp4"
                                ),
                                prompt,
                            ],
                        ).text
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.code(prompt, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: Video Highlights
    # -------------------------------------------------------------------
    with video_highlights:
        st.markdown(
            """Below is another example of using Gemini to ask questions about objects, people or the context, as shown in the video about Pixel 8 below:"""
        )
        video_highlights_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/pixel8.mp4"

        if video_highlights_uri:
            st.video(video_highlights_uri)
            st.write("Our expectation: Generate the highlights for the video")
            # Ask specific questions about people, product features, and request a summary
            prompt = """Answer the following questions using the video only:
What is the profession of the girl in this video?
Which all features of the phone are highlighted here?
Summarize the video in one paragraph.
Provide the answer in table format.
      """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_highlights_description = st.button(
                "Generate video highlights", key="video_highlights_description"
            )
            with tab1:
                if video_highlights_description and prompt:
                    with st.spinner(
                        f"Generating video highlights using {get_model_name(selected_model)} ..."
                    ):
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=[
                                Part.from_uri(
                                    file_uri=video_highlights_uri, mime_type="video/mp4"
                                ),
                                prompt,
                            ],
                        ).text
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.code(prompt, language="markdown")

    # -------------------------------------------------------------------
    # Sub-tab: Video Geolocation
    # -------------------------------------------------------------------
    with video_geolocation:
        st.markdown(
            """Even in short, detail-packed videos, Gemini can identify the locations."""
        )
        video_geolocation_uri = "https://storage.googleapis.com/github-repo/img/gemini/multimodality_usecases_overview/bus.mp4"

        if video_geolocation_uri:
            st.video(video_geolocation_uri)
            st.markdown(
                """Our expectation: \n
      Answer the following questions from the video:
        - What is this video about?
        - How do you know which city it is?
        - What street is this?
        - What is the nearest intersection?
      """
            )
            # Ask the model to identify location from visual clues in the video
            # (street signs, landmarks, bus numbers, architecture, etc.)
            prompt = """Answer the following questions using the video only:
      What is this video about?
      How do you know which city it is?
      What street is this?
      What is the nearest intersection?
      Answer the following questions in a table format with question and answer as columns.
      """
            tab1, tab2 = st.tabs(["Response", "Prompt"])
            video_geolocation_description = st.button(
                "Generate", key="video_geolocation_description"
            )
            with tab1:
                if video_geolocation_description and prompt:
                    with st.spinner(
                        f"Generating location tags using {get_model_name(selected_model)} ..."
                    ):
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=[
                                Part.from_uri(
                                    file_uri=video_geolocation_uri,
                                    mime_type="video/mp4",  # Tell the API this is an MP4 video
                                ),
                                prompt,
                            ],
                        ).text
                        st.markdown(response)
                        st.markdown("\n\n\n")
            with tab2:
                st.write("Prompt used:")
                st.code(prompt, language="markdown")
