# Text Input Feature - Documentation

## Overview

The Math Agent System now supports direct text input for math problems and equations. Users can enter problems directly without needing to upload a PDF file.

## New Features

### 1. Text Input Endpoint

**Endpoint:** `POST /solve-text`

**Request Body:**
```json
{
  "text": "What is the probability of rolling a 6 on a fair die?",
  "problem_type": "probability"  // Optional - auto-detected if not provided
}
```

**Response:**
```json
{
  "explanation": "...",
  "steps": ["...", "..."],
  "matlab_code": "...",
  "latex_solution": "...",
  "confidence": 0.9,
  "problem_type": "probability"
}
```

### 2. Text Processor Service

A new `TextProcessor` service (`app/services/text_processor.py`) that:
- Extracts equations from text input
- Auto-detects problem types (probability, statistics, algebra, calculus, linear algebra, general)
- Extracts LaTeX expressions (between $ signs)
- Identifies mathematical equations in various formats

### 3. Web Interface Updates

The web interface now includes:
- A text input form at the top of the page
- Textarea for entering problems or equations
- Optional problem type selector
- Real-time solving with loading indicators

## Supported Problem Types

Currently supported (with agents):
- ✅ **Probability** - Fully supported
- ✅ **Statistics** - Fully supported

Auto-detected but not yet supported (no agents yet):
- ⏳ **Algebra** - Detected but needs agent
- ⏳ **Calculus** - Detected but needs agent
- ⏳ **Linear Algebra** - Detected but needs agent
- ⏳ **General** - Detected but needs agent

## Usage Examples

### Example 1: Probability Problem
```json
POST /solve-text
{
  "text": "What is the probability of rolling a 6 on a fair die?"
}
```

### Example 2: With Explicit Type
```json
POST /solve-text
{
  "text": "A coin is flipped 3 times. What is the probability of getting exactly 2 heads?",
  "problem_type": "probability"
}
```

### Example 3: Equation with LaTeX
```json
POST /solve-text
{
  "text": "Solve: $x^2 + 5x + 6 = 0$"
}
```

## Equation Detection

The text processor can detect:
- Simple equations: `x = 5`, `y = 2x + 3`
- Function definitions: `f(x) = x^2 + 1`
- Integrals: `∫ x^2 dx`
- Derivatives: `d/dx (x^2)`

## Problem Type Detection

The system automatically detects problem types based on keywords:

- **Probability**: probability, random, distribution, expected value, variance, binomial, normal, poisson
- **Statistics**: mean, median, mode, hypothesis, confidence interval, regression, t-test
- **Calculus**: derivative, integral, limit, differentiate, integrate, d/dx
- **Linear Algebra**: matrix, vector, eigenvalue, determinant, basis, span
- **Algebra**: solve, equation, simplify, factor, quadratic, polynomial, root

## Testing

Run the test script to verify functionality:
```bash
python test_text_input.py
```

## API Documentation

Visit http://127.0.0.1:8000/docs to see the interactive API documentation with the new endpoint.

## Future Enhancements

- [ ] Add support for image uploads with equations
- [ ] Support for multi-line equations
- [ ] Equation validation and parsing
- [ ] Support for more problem types (algebra, calculus agents)
- [ ] Natural language to equation conversion

