import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import math


# Configuration
DATA_URL = "https://dev.cosmi.skin/admin/get-image"  # Replace with your data source URL
POST_API_URL = "https://dev.cosmi.skin/admin/save-image"  # Replace with your POST API URL
ITEMS_PER_PAGE = 8  # Number of images per page

# Function to fetch image URLs and total count from the data source
@st.cache_data
def fetch_images(offset, limit):
    try:
        response = requests.get(
            DATA_URL,
            headers={"Authorization": "Bearer zardam@gmail.com"},
            params={"offset": offset, "limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        images = [(d["skincare_id"], d['image'], d.get('is_marked', False)) for d in data['data']]  # Adjust based on API response
        total = data.get('total_images', 0)  # Assuming the API returns total count
        return images, total
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return [], 0

# Function to fetch an image from a URL
def get_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading image: {e}")
        return None

# Initialize session state for pagination
if 'page' not in st.session_state:
    st.session_state.page = 1

if 'rated_images' not in st.session_state:
    st.session_state.rated_images = set()

# Calculate offset based on current page
current_page = st.session_state.page
offset = (current_page - 1) * ITEMS_PER_PAGE
limit = ITEMS_PER_PAGE

# Fetch images and total count
image_urls, total_images = fetch_images(offset, limit)
total_pages = math.ceil(total_images / ITEMS_PER_PAGE) if ITEMS_PER_PAGE else 1

# Pagination Controls
col_prev, col_page, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("Previous") and current_page > 1:
        st.session_state.page -= 1

with col_next:
    if st.button("Next") and current_page < total_pages:
        st.session_state.page += 1

st.markdown(f"**Page {current_page} of {total_pages}**")

st.markdown("### Image Ratings")

rows = 2
cols_per_row = 4
for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_index, col in enumerate(cols):
        idx = row * cols_per_row + col_index
        if idx < len(image_urls):
            skincare_id, img_url, is_marked = image_urls[idx]

            # Check if the image has been rated in the current session
            if is_marked == False and skincare_id in st.session_state.rated_images:
                is_marked = True

            with col:
                st.markdown(f"**Image {offset + idx + 1}**")
                image = get_image(img_url)
                if image:
                    st.image(image, use_container_width=True)

                if is_marked:
                    st.success("**Already Rated**")
                else:
                    with st.form(key=f"form_{skincare_id}"):
                        st.write("**Rate the following facial features:**")
                        oiliness = st.slider("Oiliness", 0, 100, 50, key=f"oiliness_{skincare_id}")
                        acne = st.slider("Acne", 0, 100, 50, key=f"acne_{skincare_id}")
                        pores = st.slider("Pores", 0, 100, 50, key=f"pores_{skincare_id}")
                        skin_tone = st.slider("Skin Tone", 0, 100, 50, key=f"skin_tone_{skincare_id}")
                        hydration = st.slider("Hydration", 0, 100, 50, key=f"hydration_{skincare_id}")
                        wrinkle = st.slider("Wrinkle", 0, 100, 50, key=f"wrinkle_{skincare_id}")
                        redness = st.slider("Redness", 0, 100, 50, key=f"redness_{skincare_id}")
                        dark_circles = st.slider("Dark Circles", 0, 100, 50, key=f"dark_circles_{skincare_id}")
                        skin_age = st.slider("Skin Age", 0, 100, 50, key=f"skin_age_{skincare_id}")
                        
                        submit_button = st.form_submit_button(label='Submit')

                        if submit_button:
                            payload = {
                                "skincare_id": skincare_id,
                                "human_score": {
                                    "Oiliness": oiliness,
                                    "Acne": acne,
                                    "Pores": pores,
                                    "Skin Tone": skin_tone,
                                    "Hydration": hydration,
                                    "Wrinkle": wrinkle,
                                    "Redness": redness,
                                    "Dark Circles": dark_circles,
                                    "Skin Age": skin_age
                                }
                            }
                            
                            try:
                                post_response = requests.post(
                                    POST_API_URL, 
                                    json=payload, 
                                    headers={"Authorization": "Bearer zardam@gmail.com"}  # Replace with your actual token if needed
                                )
                                post_response.raise_for_status()
                                st.success(f"Data for Image {offset + idx + 1} submitted successfully!")
                                # Update local state to mark the image as rated
                                st.session_state.rated_images.add(skincare_id)
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to submit data: {e}")
                
                st.markdown("---")

# Optionally, display a message if no images are available
if total_images == 0:
    st.warning("No images available to display.")
