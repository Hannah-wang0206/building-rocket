Initial Concept - Frontend and Backend Version
Overview
This project represents the initial concept of both the frontend and backend for a web-based application. The project was developed to demonstrate the design and functionality of a web interface and server-side operations for generating images based on user input.

Timeline
Early November: The project concept and plan were finalized, including the design of the web interface.
Mid November: The frontend HTML code for the pages was completed, allowing for the basic layout and functionality of the pages. However, during this phase, we encountered issues with the communication between the frontend and backend.
Current Status
As of now, the frontend and backend are not communicating correctly. While the frontend correctly renders the pages, and image generation works fine in terms of backend processing, the generated images are not being displayed on the frontend. Specifically, the image generation functionality operates correctly when inspected in F12 Developer Tools, but the generated image fails to appear on the webpage.

Solution
Due to the communication issues between the frontend and backend, we decided to pivot and use Streamlit as the final presentation tool. Streamlit allows us to quickly deploy and display the functionalities of the application without dealing with the complexities of frontend-backend communication issues.