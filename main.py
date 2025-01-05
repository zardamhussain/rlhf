import json
import streamlit as st # type: ignore
import requests
import math
from storage import list_images, get_image
from db import update_image_labled

# Configuration
ITEMS_PER_PAGE = 8  # Number of images per page

# Function to fetch image URLs and total count from the data source
@st.cache_data
def fetch_images(offset, limit):
    # returns total, [(image_id, isLabled)]
    return list_images(offset, limit)


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
total_images, image_ids = fetch_images(offset, limit)
total_pages = math.ceil(total_images / ITEMS_PER_PAGE) if ITEMS_PER_PAGE else 1

# Pagination Controls
col_prev, col_page, col_next = st.columns([1, 2, 1])


def decrement_page():
    st.session_state.page -= 1

def increment_page():
    st.session_state.page += 1

with col_prev:
    prev_disabled = current_page <= 1
    if st.button("Previous", key="prev_button", disabled=prev_disabled, on_click=decrement_page):
        pass
    
with col_next:
    next_disabled = current_page >= total_pages
    if st.button("Next", key="next_button", disabled=next_disabled, on_click=increment_page):
        pass

st.markdown(f"**Page {current_page} of {total_pages}**")

st.markdown("### Image Ratings")

rows = 2
cols_per_row = 4
for row in range(rows):
    cols = st.columns(cols_per_row)
    for col_index, col in enumerate(cols):
        idx = row * cols_per_row + col_index
        if idx < len(image_ids):
            image_id, image_data = image_ids[idx]

            is_marked = image_data.get("isLabled", False)

            # Check if the image has been rated in the current session
            if is_marked == True or image_id in st.session_state.rated_images:
                is_marked = True

            with col:
                st.markdown(f"**Image {offset + idx + 1}**")
                image = get_image(image_id)
                if image:
                    st.image(image, use_container_width=True)

                if is_marked:
                    st.success("**Already Rated**")
                else:
                    with st.form(key=f"form_{image_id}"):
                        llm_response = json.loads(image_data["llm_response"])
                        st.write("**Rate the following facial features:**")
                        oiliness = st.slider("Oiliness", 0, 100, int(llm_response.get("Oiliness", 50)), key=f"oiliness_{image_id}")
                        acne = st.slider("Acne", 0, 100, int(llm_response.get("Acne", 50)), key=f"acne_{image_id}")
                        pores = st.slider("Pores", 0, 100, int(llm_response.get("Pores", 50)), key=f"pores_{image_id}")
                        skin_tone = st.slider("Skin Tone", 0, 100, int(llm_response.get("Skin Tone", 50)), key=f"skin_tone_{image_id}")
                        hydration = st.slider("Hydration", 0, 100, int(llm_response.get("Hydration", 50)), key=f"hydration_{image_id}")
                        wrinkle = st.slider("Wrinkle", 0, 100, int(llm_response.get("Wrinkle", 50)), key=f"wrinkle_{image_id}")
                        redness = st.slider("Redness", 0, 100, int(llm_response.get("Redness", 50)), key=f"redness_{image_id}")
                        dark_circles = st.slider("Dark Circles", 0, 100, int(llm_response.get("Dark Circles", 50)), key=f"dark_circles_{image_id}")
                        skin_age = st.slider("Skin Age", 0, 100, int(llm_response.get("Skin Age", 50)), key=f"skin_age_{image_id}")
                        
                        submit_button = st.form_submit_button(label='Submit')

                        if submit_button:
                            payload = {
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
                            
                            try:
                                update_image_labled(image_id, True, payload)
                                st.success(f"Data for Image {offset + idx + 1} submitted successfully!")
                                # Update local state to mark the image as rated
                                st.session_state.rated_images.add(image_id)
                                st.rerun()
                            except requests.exceptions.RequestException as e:
                                st.error(f"Failed to submit data: {e}")
                
                st.markdown("---")

# Optionally, display a message if no images are available
if total_images == 0:
    st.warning("No images available to display.")
