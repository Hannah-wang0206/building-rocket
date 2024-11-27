import streamlit as st
import requests
import replicate
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import date

# Replicate API setup
replicate_client = replicate.Client(api_token="r8_MeFEKgscN4NYt96L0Z4awdKSCFeEw4d3fUO")


# Constants for distances (in meters)
celestial_bodies = {
    "Moon": {"distance": 384400000},  # Distance from Earth (in meters)
    "Venus": {"distance": 108200000000},  # Distance from the Sun (in meters)
    "Mars": {"distance": 227940000000},  # Distance from the Sun (in meters)
    "Earth": {"distance": 149600000000},  # Distance from the Sun (in meters)
}

# Function to calculate and plot the orbit
def plot_orbit(target="Moon", angle=45, velocity=8000, fuel=500):
    try:
        # Get target data
        target_data = celestial_bodies[target]
        r_target = target_data["distance"]

        # Low Earth Orbit (LEO) radius (700 km above Earth's surface) - scaled up by 1000x
        r_low_orbit = 7000000 * 1000  # Low Earth orbit radius in meters (700 km above surface, scaled)
        r_earth = celestial_bodies["Earth"]["distance"]  # Distance of Earth from the Sun (in meters)
        r_sun = 0  # Sun is at the origin (0, 0)

        # Calculate the semi-major axis for the transfer orbit (from Earth to target)
        a_transfer = (r_earth + r_target) / 2  # Average of Earth and target distance
        angle_rad = np.radians(angle)  # Convert angle to radians
        velocity_orbit = velocity * np.cos(angle_rad)  # Adjust velocity along the orbit

        # Adjust semi-major axis and eccentricity based on velocity and fuel
        a_transfer = a_transfer * (velocity_orbit / velocity) * (1 + fuel / 1000)
        e_transfer = 1 - (r_earth / a_transfer)  # Simplified eccentricity calculation

        # Create figure and axis for plotting
        fig, ax = plt.subplots(figsize=(8, 8))

        # Adjust limits to ensure all celestial bodies and their orbits are visible
        max_distance = max(celestial_bodies['Venus']['distance'], celestial_bodies['Mars']['distance'],
                           celestial_bodies['Earth']['distance'])
        ax.set_xlim(-max_distance * 1.5, max_distance * 1.5)
        ax.set_ylim(-max_distance * 1.5, max_distance * 1.5)

        # Plot Earth at the center (0, 0)
        ax.plot(0, 0, "bo", label="Earth")

        # Plot Low Earth Orbit (LEO) around Earth (fixed distance)
        ax.plot(r_low_orbit * np.cos(np.linspace(0, 2 * np.pi, 100)),
                r_low_orbit * np.sin(np.linspace(0, 2 * np.pi, 100)), 'k--', label="Low Earth Orbit")

        # Plot the transfer orbit (ellipse between Earth and target)
        theta = np.linspace(0, 2 * np.pi, 100)
        x_transfer = a_transfer * np.cos(theta)
        y_transfer = a_transfer * np.sin(theta)
        ax.plot(x_transfer, y_transfer, 'r--', label="Transfer Orbit")

        # Plot the target body as a point on the plot
        if target == 'Moon':
            ax.plot(r_target, 0, "go", label="Moon")  # Moon in green
            ax.plot(r_target * np.cos(np.linspace(0, 2 * np.pi, 100)),
                    r_target * np.sin(np.linspace(0, 2 * np.pi, 100)), 'g--', label="Moon Orbit")

        elif target == 'Venus' or target == 'Mars':
            sun_x = r_earth + 50000000000  # Set the Sun's x-coordinate far from Earth
            sun_y = 0  # Sun's y-coordinate at 0

            # Plot the orbit of Venus or Mars around the Sun (full orbit)
            theta_planet = np.linspace(0, 2 * np.pi, 100)
            if target == 'Venus':
                x_planet = r_target * np.cos(theta_planet) + sun_x
                y_planet = r_target * np.sin(theta_planet)
                ax.plot(x_planet, y_planet, 'm--', label="Venus Orbit")
                ax.plot(r_target + sun_x, 0, "yo", label="Venus")
            elif target == 'Mars':
                x_planet = r_target * np.cos(theta_planet) + sun_x
                y_planet = r_target * np.sin(theta_planet)
                ax.plot(x_planet, y_planet, 'b--', label="Mars Orbit")
                ax.plot(r_target + sun_x, 0, "bo", label="Mars")

        ax.set_aspect("equal", "box")
        ax.set_xlabel("X Position (m)")
        ax.set_ylabel("Y Position (m)")
        ax.set_title(f"Orbital Path to {target}")
        ax.legend()

        # Show plot in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error generating orbit: {e}")


# AI Image Generation Section at the top
st.title("SYNTHESIS SPACE PROGRAM 🧑‍🚀")
st.header("AI Image Generation")
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png/1200px-Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png"  # 替换为实际图片的URL或本地路径
st.image(image_url, use_container_width=True)
uploaded_image = st.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"])
prompt = st.text_input("Enter a description (prompt):", "a photo of a real rocket")

if st.button("Generate AI Image"):
    if uploaded_image and prompt:
        try:
            temp_file_path = "../temp_uploaded_image.png"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_image.read())

            with open(temp_file_path, "rb") as image_file:
                input_data = {"image": image_file, "prompt": prompt}
                st.write("Generating images...")
                output = replicate_client.run(
                    "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                    input=input_data,
                )

            st.header("Generated Images")
            for index, item in enumerate(output):
                image_response = requests.get(item)
                output_image = Image.open(BytesIO(image_response.content))
                st.image(output_image, caption=f"Output Image {index + 1}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image and enter a prompt.")

# Orbital Path Visualization Section
st.header("Orbital Path Parameters")

# Create 4 horizontal columns for images
col1, col2, col3, = st.columns(3)

# You can display images like this:
image_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png/1200px-Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png",  # Replace with actual image URLs
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png/1200px-Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png/1200px-Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png",
]

# Loop to display images in columns
with col1:
    st.image(image_urls[0], caption="Moon")
with col2:
    st.image(image_urls[1], caption="Venus")
with col3:
    st.image(image_urls[2], caption="Mars")

# Target selection
target = st.selectbox("Select Target Planet", ["Moon", "Venus", "Mars"])

# User input for velocity (in m/s), angle (in degrees), and fuel (in arbitrary units)
angle = st.slider("Launch Angle (degrees)", 0, 90, 45)
velocity = st.slider("Launch Velocity (m/s)", 3000, 15000, 8000)
fuel = st.slider("Fuel Amount (arbitrary units)", 100, 1000, 500)

# Apply limits and display warning if needed
if target == "Moon":
    if velocity < 5000 or velocity > 12000:
        st.warning("Warning: For Moon, launch velocity should be between 5000 m/s and 12000 m/s.")
    if angle < 10 or angle > 80:
        st.warning("Warning: For Moon, launch angle should be between 10° and 80°.")
    if fuel < 200 or fuel > 900:
        st.warning("Warning: For Moon, fuel amount should be between 200 and 900 units.")
elif target == "Venus" or target == "Mars":
    if velocity < 10000 or velocity > 30000:
        st.warning(f"Warning: For {target}, launch velocity should be between 10000 m/s and 30000 m/s.")
    if angle < 20 or angle > 70:
        st.warning(f"Warning: For {target}, launch angle should be between 20° and 70°.")
    if fuel < 300 or fuel > 1000:
        st.warning(f"Warning: For {target}, fuel amount should be between 300 and 1000 units.")

# Plot the selected target orbit based on user input
plot_orbit(target=target, angle=angle, velocity=velocity, fuel=fuel)

# Rocket Launch Control Center Section at the bottom
st.header("Rocket Launch Control Center 🚀")

# Rocket input section
rocket_name = st.text_input("Enter rocket name:", placeholder="e.g., Long March 5")
launch_date = st.date_input("Select launch date:", min_value=date.today())

# Launch button
if st.button("Launch Rocket 🚀"):
    if rocket_name and launch_date:
        st.success(f"Mission Complete! Rocket **{rocket_name}** is successfully scheduled for launch on **{launch_date}**!")
    else:
        st.warning("Please ensure rocket name and launch date are entered.")
