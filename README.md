# ChatGPT Market Analysis with OpenAI API

This project utilizes the OpenAI GPT-4 model to perform market analysis based on customer feedback and other business data. It provides an interactive chat interface for users to query and analyze datasets related to business performance and customer satisfaction.

## Features

- Upload and process datasets (txt, xlsx, csv formats supported)
- Interactive chat interface for querying the dataset
- Utilizes OpenAI's GPT-4 model for intelligent analysis
- Tracks and displays API usage costs
- Maintains chat history for context in follow-up questions

## Requirements

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chatgpt-market-analysis.git
   cd chatgpt-market-analysis
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

### Option 1: Run the Python Script

1. Run the script:
   ```
   python market_analysis.py
   ```

2. Follow the prompts to upload your dataset and start the analysis.

3. Enter your queries about the dataset when prompted. The AI will analyze the data and provide insights based on your questions.

4. Type 'q', 'quit', or 'exit' to end the session and see the total API usage cost.

### Option 2: Use Google Colab (Recommended for Easier Usage)

1. Open the Jupyter notebook file located in the `notebooks` folder using Google Colab.

2. Follow the instructions in the notebook to set up your API key and upload your dataset.

3. Run the cells in the notebook to interact with the ChatGPT Market Analysis tool.

This method provides a more user-friendly interface and doesn't require local Python installation or setup.

## Note

This project uses the OpenAI API, which incurs costs based on usage. Monitor your usage and set appropriate limits to avoid unexpected charges.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.