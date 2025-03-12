# Clipboard Health Marketplace Analysis

A comprehensive analysis suite for Clipboard Health's marketplace data, providing insights into worker behavior, workplace engagement, and overall marketplace dynamics.

## Overview

This project analyzes shift-offer data from a marketplace, where each row represents a single "shift offer," including metadata such as:

- `shift_id`
- `worker_id`
- `workplace_id`
- `shift_start_at`
- `shift_created_at`
- `offer_viewed_at`
- `rate`
- `charge_rate`
- `duration`
- `slot`
- `claimed_at`
- `canceled_at`
- `deleted_at`
- `is_ncns`
- `is_verified`

The analysis is organized into modular components:

- `core.py`: Core utilities and data loading functions
- `worker_analysis.py`: Worker-focused analysis, including metrics, segmentation, and retention
- `workplace_analysis.py`: Workplace-focused analysis, including metrics, repeat bookings, and deletions
- `shift_analysis.py`: Shift and pricing analysis, including price sensitivity, cancellations, and more
- `ai_analysis.py`: OpenAI-powered advanced analysis using large language models
- `main.py`: The main execution script that runs the full analysis workflow

## Getting Started

### Prerequisites

- Python 3.8+
- Required packages (install with `pip`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - scikit-learn
  - statsmodels
  - pyyaml

### Running the Analysis

Place your data file in the root directory as `data.csv` and run:

```bash
python main.py
```

Optionally, you can provide a data dictionary file as `data_dictionary.yml` for better field descriptions.

## Output

The analysis generates the following outputs in the `output` directory:

- `detailed_analysis.md`: Comprehensive analysis of all metrics
- `summary_report.md`: High-level summary of key findings
- `plots/`: Visualizations of various metrics
- `tables/`: CSV files with detailed data for each analysis

## Optional AI Analysis

The tool can optionally use OpenAI's O1 model to generate additional insights. To use this feature:

1. Set your OpenAI API key as an environment variable: `export OPENAI_API_KEY=your-key-here`
2. Or place your API key in a file named `openai_api_key.txt` in the project root

## Analysis Components

The analysis covers:

1. **Worker Metrics**: Acceptance rates, earnings distribution, power worker identification
2. **Workplace Metrics**: Fill rates, problematic workplaces, workplace stickiness
3. **Price Sensitivity**: How pay rates affect claim rates and no-show rates
4. **Shift Types**: Preference patterns for different shift slots and times
5. **Cancellations**: When and why workers cancel shifts
6. **Time Metrics**: Decision time analysis, lead time impacts
7. **Worker Segmentation**: Clustering workers by behavior patterns
8. **Repeat Bookings**: Analyzing worker loyalty to workplaces
9. **Shift Deletions**: Understanding when and why shifts get deleted
10. **Dynamic Pricing**: Impact of rate changes on worker claiming behavior