# STL Property Enforcement Experiment Reproduction

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the implementation and reproduction package for the experiments presented in the paper **"Runtime Enforcement of CPS against Signal Temporal Logic"**. The project focuses on runtime enforcement of STL properties using transducer-based monitoring.

## Prerequisites

- Docker Environment Requirements

| Component       | Tested Version | Minimum Required |  Download Links |
|-----------------|----------------|-------------------|----------------|
| Docker Engine   | 27.4.0         | 20.10.14+         | [Get Docker](https://docs.docker.com/engine/install/) |
| Docker Compose  | 2.31.0         | 2.17.0+           | [Compose Docs](https://docs.docker.com/compose/install/) |

- Git (for cloning the repository)
- 4GB+ free disk space

## Reproduction Steps

#### Method 1: Docker-Based Execution (Recommended)
##### 1. Clone repository
```bash
git clone https://github.com/Han-SU/stl-enforcement-experiments.git
cd stl-enforcement-experiments
```

##### 2. Build Docker image
```bash
docker-compose build
```

##### 3. Run experiments
```bash
docker-compose up
```
##### 4. Modify source code and re-run (when needed)
Edit files in src/ directory then:
```bash
docker-compose restart re-stl
```

##### 5. View results
Results will be generated in the `res` directory.

#### Method 2: Local Execution
##### 1. Install Python 3.12.4 (required)
Using pyenv recommended:
```bash
pyenv install 3.12.4
pyenv local 3.12.4
```
##### 2. Install dependencies
```bash
pip install numpy==1.26.4 matplotlib==3.8.2
```
##### 3. Run experiments
```bash
chmod +x run_local.sh
./run_local.sh
```
#### Compatibility Notes:

- Verified on Python 3.12.4 only
- May require additional system libraries
- Results may vary across different OS/hardware





