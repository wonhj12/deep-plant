# Use the official nginx image as a parent image
FROM nginx:stable

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom nginx.conf to the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to the outside
EXPOSE 80

# Start nginx when the container is launched
CMD ["nginx", "-g", "daemon off;"]
