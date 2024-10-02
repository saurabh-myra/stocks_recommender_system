
# Flask Application with Docker

This repository contains a Flask application that can be run locally using Docker and deployed to Azure App Service using Azure Container Registry.

## Prerequisites

- Docker installed on your local machine
- Azure CLI installed and configured
- An Azure account with access to Azure App Service and Azure Container Registry (ACR)

## Running the Application Locally

### Step 1: Build the Docker Image

Navigate to the project directory containing the Dockerfile and run the following command to build the Docker image:

```sh
docker build -t flask-app .
```

### Step 2: Run the Docker Container

Run the Docker container, mapping port 5051 in the container to port 5051 on your local machine:

```sh
docker run -d -p 5051:5051 flask-app
```

### Step 3: Access the Application

Open a web browser and navigate to `http://localhost:5051`. You should see the output of your Flask application.

## Deploying the Application to Azure

### Step 1: Login to Azure CLI

Open your terminal and login to Azure using Azure CLI:

```sh
az login
```

### Step 2: Login to Azure Container Registry

Replace `myContainerRegistry` with your actual ACR name:

```sh
az acr login --name myContainerRegistry
```

### Step 3: Build and Push Docker Image

1. **Build Docker Image**:

   ```sh
   docker build -t flask-app .
   ```

2. **Tag Docker Image**:

   Replace `myContainerRegistry` with your actual ACR name:

   ```sh
   docker tag flask-app myContainerRegistry.azurecr.io/flask-app:v1
   ```

3. **Push Docker Image**:

   ```sh
   docker push myContainerRegistry.azurecr.io/flask-app:v1
   ```

### Step 4: Configure Azure App Service

1. **Navigate to Your App Service**:
   - Go to the [Azure Portal](https://portal.azure.com/).
   - In the left-hand menu, select **App Services**.
   - Click on your App Service instance (e.g., `StockRecommendation`).

2. **Open Deployment Center**:
   - In the left-hand menu under **Deployment**, click on **Deployment Center**.

3. **Configure Docker Container**:
   - In the **Settings** tab, select **Container Registry**.
   - Choose **Azure Container Registry** as the image source.
   - Select your Azure Container Registry (`myContainerRegistry`).
   - Select your repository (`flask-app`) and the tag (`v1`).

4. **Authentication**:
   - Select **Admin Account**.
   - Enter the **Username** and **Password** from the ACR **Access keys** section.

5. **Apply Configuration**:
   - Click **Save** or **Apply** to save the configuration.

6. **Set Application Settings**:
   - In the left-hand menu under **Settings**, click on **Configuration**.
   - Add or ensure the following application setting is present:
     - `WEBSITES_PORT` set to `5051`.
   - Click **Save** to apply the changes.

7. **Restart Your App Service**:
   - In the left-hand menu, click on **Overview**.
   - Click **Restart** to restart your app with the new Docker image configuration.

### Step 5: Validate Deployment

1. **Check Application Logs**:
   - In Azure Portal, go to **App Services**.
   - Click on your web app.
   - Under **Monitoring**, click on **Log Stream** to view real-time logs.

2. **Access Your Application**:
   - Open your browser and navigate to the URL of your App Service. It should be in the format:
     ```
     http://<your-app-service-name>.azurewebsites.net
     ```
   - For example, `http://stockrecommendation.azurewebsites.net`.

## Troubleshooting

- **Authentication Issues**:
  Ensure you have the correct username and password for the Azure Container Registry.
  
- **Port Configuration**:
  Ensure `WEBSITES_PORT` is set to `5051` in the Azure App Service configuration.

- **Log Stream**:
  Use the log stream in Azure to monitor the application logs and identify any issues.

## Conclusion

By following these steps, you can run the Flask application both locally and on Azure App Service. If you encounter any issues, refer to the troubleshooting section or consult the official Azure documentation.
