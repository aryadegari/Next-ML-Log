# Synthetic Event Log Generation / Machine Learning on Business Process Data

Implementation of the paper "Cartwright, D., Sterie, R.A., Yadegari Ghahderijani, A., Karastoyanova, D.: Adaptive Process Log Generation and Analysis
with Next Log and ML Log" submitted to [EDOC 2023 Demonstration Track](https://www.rug.nl/research/bernoulli/conf/edoc-2023/call-for-papers/call-for-demonstration?lang=en).

### Project Description

This desktop app is a combination of both of our thesis projects; 

To get a better overview of the programs, click the "Info" page inside each program.

#### 1. next(log)

The objective of this project is to develop a sophisticated tool for generating logs that can be used with adaptive business processes. The goal is to create logs for a variety of process models and adaptations, thereby facilitating the effective testing and evaluation of these processes. The user can create datasets based on rules they define. 

#### 2. ML.log

The objective of this project is to utilize machine learning algorithms on adaptive business process logs to identify correlations in a way that builds upon existing experiments. The project seeks to develop insights into business processes . To achieve this objective, the project will employ various machine learning techniques to analyse sets of adaptive business process data and identify patterns.

### Demostration Video
The [Demonstration Video](https://doi.org/10.6084/m9.figshare.24082083.v1) explains briefly how the tool works and shows some of its features.


### Running the program

1. Install Python 3.11+
2. Install Graphviz.
3. Unzip the given .zip file. 
4. Create a venv.
5. Install the required libraries.
6. Fix a small bug in one of the libraries.
7. Run main.py.

###### For Windows;

1. [Download Python | Python.org](https://www.python.org/downloads/)

2. [Download | Graphviz](https://graphviz.org/download/#windows)
   
   Make sure you add it to the path; [StackOverflow explanation](https://stackoverflow.com/a/44005139/21256109)

3. Unzip the folder. Let's assume it's called Thesis_LogGenerator.

4. Create venv and activate; <br/>
   ```cd Thesis_LogGenerator ```; <br/> 
   ```python -m venv venv```; <br/>
   ```venv\Scripts\activate```. <br/>
    Again, make sure you're using Python 3.11+ (`python --version`).

5. Install required libraries: ```pip install -r requirements.txt```.

6. There is a small bug in one of the libraries. ```cd venv/Lib/site-packages/sklvq/models```, find the file called ```_base.py``` and replace line 691 with the following instead <br/>
```return self.classes_[(decision_values > 0).astype(int)]```. 

7. Run the program. ```python main.py```. 
   
   Note it takes a few seconds to start the first time.



###### For Mac;

1. [Download Python | Python.org](https://www.python.org/downloads/)

2. [Install Graphviz - use instructions here](https://stackoverflow.com/a/75540978/21256109). 
   
   You might need to add MacPorts to Path with:<br/>
   ```export PATH="/opt/local/bin:$PATH"```<br/>
   before being able to use ```sudo port```.

3. Run; ```brew install python-tk```. // Assuming you have homebrew, if not; ```https://brew.sh/```. 

4. Unzip the folder. Let's assume it's called Thesis_LogGenerator.

5. Create venv and activate; <br/>
   `cd Thesis_LogGenerator` ; <br/>
   `python -m venv venv`;  <br/>
   `source venv/bin/activate`. <br/>
   Again, make sure you're using Python 3.11+ (```python --version```).

6. Install required libraries: `pip install -r requirements.txt`.

7. There is a small bug in one of the libraries. `cd venv/lib/python3.11/site-packages/sklvq/models`, find the file called `_base.py` and replace line 691 with the following instead <br/>
 `return self.classes_[(decision_values > 0).astype(int)]`.

8. Run the program. `python main.py`. 
   
   Note it takes a few seconds to start the first time.

---

_Authors: Dyllan Cartwright & Radu Sterie & Arash Yadegari (University of Groningen)._
