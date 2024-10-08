
# Drug Dashboard

## Overview

The Drug Dashboard is an interactive web application built with Dash that allows users to analyze data related to controlled prescription drugs in Michigan. The dashboard features an AI agent that can generate tables, create charts, and provide insights based on the provided data.

## Data Source

The data for the dashboard is sourced from the Michigan Department of Licensing and Regulatory Affairs. You can find the data [here](https://www.michigan.gov/lara/bureau-list/bpl/health/maps/reports). This dataset includes information on prescription data across different regions, patient demographics, and prescription characteristics.

## Requirements

- Docker
- An `.env` file with the following environment variable:
  - `OPENAI_API_KEY` (required for AI analysis)

## Getting Started

### Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### Build the Docker Image

To build the Docker image for the dashboard, run the following command in the project directory:

```bash
docker build -t drug-dashboard .
```

### Run the Dashboard

Once the image is built, you can run the dashboard using Docker. Use the command below, making sure to map your local data directory:

```bash
docker run -v ./data:/app/data -p 8050:8050 drug-dashboard
```

### Access the Dashboard

After running the Docker container, you can access the dashboard by opening your web browser and navigating to `http://localhost:8050`.

## AI Analysis

The AI agent in the dashboard is designed to analyze the provided data. Ensure that the `.env` file containing your `OPENAI_API_KEY` is located in the project directory. This key is necessary for the AI functionalities.

## Preview
![dashboard](resources/dashboard.gif)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please create a pull request or open an issue.
