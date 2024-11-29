import streamlit as st
import requests
import replicate
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Flask server configuration
FLASK_SERVER_URL = "http://14.136.11.131:5000"  # 替换为实际的公网 IP

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

# Streamlit UI
st.title("Orbital Path Visualization")
st.sidebar.header("Input Parameters")

# Target selection
target = st.sidebar.selectbox("Select Target Planet", ["Moon", "Venus", "Mars"])

# User input for velocity (in m/s), angle (in degrees), and fuel (in arbitrary units)
angle = st.sidebar.slider("Launch Angle (degrees)", 0, 90, 45)
velocity = st.sidebar.slider("Launch Velocity (m/s)", 3000, 15000, 8000)
fuel = st.sidebar.slider("Fuel Amount (arbitrary units)", 100, 1000, 500)

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

# Image Upload with Public URL Generation Section
st.header("Upload an image to get a public URL")
uploaded_image = st.file_uploader("Choose an image to upload", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    if st.button("Generate Public URL"):
        try:
            # Send the uploaded file to Flask server
            files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}
            response = requests.post(FLASK_SERVER_URL, files=files)

            if response.status_code == 200:
                public_url = response.json()["url"]
                st.success("Public URL generated successfully!")
                st.write(public_url)
                st.image(public_url, caption="Uploaded Image", use_column_width=True)
            else:
                st.error(f"Failed to upload image. Error: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Replicate API Image Generation Section
st.header("Generate Image with Replicate")

image_url = st.text_input("Enter the URL of a public image:", "https://img1.baidu.com/it/u=3813998746,3056511910&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=711")
prompt = st.text_input("Enter a description (prompt):", "a photo of a real rocket")

if st.button("Generate"):
    if image_url and prompt:
        try:
            input_data = {
                "image": image_url,
                "prompt": prompt,
            }

            # Call Replicate API with authenticated client
            st.write("Generating images...")
            output = replicate_client.run(
                "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                input=input_data,
            )

            # Display outputs
            st.header("Generated Outputs")
            for index, item in enumerate(output):
                image_response = requests.get(item)  # Fetch generated image
                output_image = Image.open(BytesIO(image_response.content))
                st.image(output_image, caption=f"Output Image {index + 1}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid image URL and prompt.")
