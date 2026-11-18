"""Re-organises scripts/v1/report_content.py into the 10-chapter layout of the sample report and writes scripts/report_content.py.
Run once:  python scripts/assemble_content.py"""
import re

src = open("scripts/v1/report_content.py", encoding="utf-8").read().replace("\r\n", "\n").split("\n")
i0 = next(i for i, l in enumerate(src) if l.startswith("def chapters"))
head, body = src[:i0], src[i0 + 1:]

# ---------- 1. cut v1 body into blocks and give every FIG/TABLE/EQ its old label ----------
blocks, cur, ch, fig, tab = {}, None, 0, 0, 0
for line in body:
    m = re.match(r'    H([12])\((?:(\d+), )?"([^"]+)"\)', line)
    if m:
        if m.group(1) == "1": ch, fig, tab = int(m.group(2)), 0, 0
        cur = m.group(3); blocks[cur] = []; continue
    if line.strip().startswith("# ====") or cur is None: continue
    if re.match(r"\s+FIG\(", line):
        fig += 1
        line = re.sub(r'(FIG\([^,]+, "[^"]*)"', rf'\1@@fig{ch}.{fig}"', line, count=1)
    elif re.match(r"\s+TABLE\(", line):
        tab += 1
        line = re.sub(r'(TABLE\("[^"]*)"', rf'\1@@tab{ch}.{tab}"', line, count=1)
    line = re.sub(r'(EQ\(.*), "(\d\.\d)"\)', r'\1, "eq\2")', line)
    blocks[cur].append(line)


def xform(lines):
    out = []
    for l in lines:
        # in-text references -> {num:key}
        def sub(m):
            kind = {"Figure": "fig", "Fig": "fig", "Table": "tab", "Equation": "eq"}[m.group(1)]
            return f"{m.group(1)}{m.group(2)} {{{{num:{kind}{m.group(3)}}}}}"
        l = re.sub(r"\b(Figure|Fig|Table|Equation)(s?) (\d\.\d+)", sub, l)
        l = re.sub(r"(\{\{num:(fig|tab|eq))(\d\.\d+)\}\} to (\d\.\d+)", lambda m: f"{m.group(1)}{m.group(3)}}}}} to {{{{num:{m.group(2)}{m.group(4)}}}}}", l)
        # chapter renumbering (old -> new)
        l = (l.replace("in Chapter 4 and Chapter 5", "in Chapter 7 and Chapters 8 and 9")
              .replace("explain the model. The project", "explain the model. The project")
              .replace("used in Chapter 3 to explain the model", "used in Chapter 5 to explain the model")
              .replace("Wilcoxon test (Chapter 4)", "Wilcoxon test (Chapter 7)")
              .replace("discussed in Chapter 4, is that", "discussed in Chapter 7, is that")
              .replace("given in Chapter 4.", "given in Chapter 7.")
              .replace("tests of Chapter 2.", "tests of Chapter 5.")
              .replace("candidates of Chapter 2.", "candidates of Chapter 5.")
              .replace("described in Chapter 2.", "described in Chapter 5."))
        out.append(l)
    return out


DROP = ("Hold-out accuracy of the three crop models", "Hold-out accuracy of the three fertilizer models")


def blk(*titles):
    lines = []
    for t in titles: lines += [l for l in blocks[t] if not any(x in l for x in DROP)]
    out = xform(lines)
    out = [l.replace(" Figure {{num:fig4.4}} compares the three models visually.", "") for l in out]
    out = [re.sub(r', 6\.0\)$', ', 4.8)', l) if "ui_" in l else l for l in out]
    return out


def sec(title, *src_titles, extra=None):
    return [f'    H2("{title}")'] + (blk(*src_titles) if src_titles else []) + (extra or [])


def sub(title, src_title):
    return [f'    H3("{title}")'] + blk(src_title)


out = []
# ---------- Chapter 1 ----------
out += ['    H1(1, "Introduction")']
out += sec("General", "Background Of The Study", "Agronomic Background Of The Inputs")
out += sec("Purpose", "Objectives")
out += sec("Scope", "Scope And Limitations")
out += sec("Motivation And Problem Statement", "Problem Statement", "Motivation")
out += sec("Datasets Used", "Datasets Used")
out += sec("Organization Of The Report", extra=['''    P("The remainder of the report is organised as follows.")
    BUL(["Chapter 2 surveys the literature on the algorithms, the evaluation methods and the tools on which the work builds.",
         "Chapter 3 analyses the functional, non-functional, hardware and software requirements of the system.",
         "Chapter 4 describes the design of the system: architecture, data flow, backend, interface and rule-based modules.",
         "Chapter 5 explains the proposed methodology: preprocessing, the algorithms, the evaluation protocol and the choice of the suitable algorithm.",
         "Chapter 6 describes the software testing, and Chapter 7 presents and discusses the experimental results.",
         "Chapters 8 and 9 give the conclusion and the future enhancements. The references, the source code, the paper publication status and the plagiarism report follow."])'''])

# ---------- Chapter 2: literature survey (new) ----------
out += ['    H1(2, "Literature Survey")']
out += ['''    P("This chapter surveys the published work on which the project builds. Because the project combines classification algorithms, "
      "statistical evaluation, data-quality checking and web deployment, the survey is organised around these four topics. Each item "
      "below states the contribution of the work and how it is used in this report.")
    H3("Classification Algorithms")
    NUM(["Quinlan {c:quinlan1986} introduced the top-down induction of decision trees using information gain, and Breiman, Friedman, Olshen and Stone {c:cart1984} "
         "developed the CART algorithm with binary splits, the Gini impurity and cost-complexity pruning. The decision tree of this project follows CART.",
         "Ho {c:ho1995} proposed building decision forests from random subsets of the features, and Breiman {c:breiman2001} combined bootstrap sampling with random "
         "feature selection and showed that the generalisation error of a forest depends on the strength of its trees and the correlation between them. "
         "The Random Forest classifier of this project is based on this work.",
         "Cover and Hart {c:cover1967} showed that the error rate of the nearest-neighbour rule is at most twice the Bayes error rate for large samples, "
         "which justifies the k-nearest-neighbour classifier used here.",
         "Cortes and Vapnik {c:cortes1995} introduced the support vector machine with the maximum-margin principle, soft margins and kernel functions; "
         "the RBF-kernel version is compared in this project.",
         "Rumelhart, Hinton and Williams {c:rumelhart1986} described back-propagation for training multilayer networks, which is the learning rule of the "
         "multilayer perceptron used here.",
         "Friedman {c:friedman2001} formulated gradient boosting as stage-wise additive modelling, and Ke et al. {c:ke2017} made boosted trees efficient with "
         "histogram-based splitting; the histogram gradient-boosting classifier follows this line of work.",
         "Hastie, Tibshirani and Friedman {c:hastie2009} give the standard treatment of the bias-variance trade-off, ensembles and model assessment that "
         "underlies the comparison of this project."])
    H3("Evaluation And Statistical Testing")
    NUM(["Kohavi {c:kohavi1995} compared cross-validation and bootstrap for accuracy estimation and recommended stratified ten-fold cross-validation "
         "for model selection. This project uses repeated stratified five-fold cross-validation.",
         "Wilcoxon {c:wilcoxon1945} proposed the signed-rank test for paired samples, and Dem\\u0161ar {c:demsar2006} recommended it for comparing two classifiers. "
         "It is used here on the paired fold scores; because folds share training data, the resulting p-values are indicative and not exact.",
         "Ojala and Garriga {c:ojala2010} described permutation tests for classifier performance, in which labels are shuffled to obtain the accuracy that "
         "would be reached by chance. The shuffled-label control of this project is of this kind."])
    H3("Data Quality And Robustness")
    NUM(["Northcutt, Athalye and Mueller {c:northcutt2021} found label errors in the test sets of ten widely used benchmarks and showed that they can change the "
         "ranking of models, which motivates the dataset audit performed here.",
         "Geirhos et al. {c:geirhos2020} described shortcut learning, in which models exploit unintended cues in a dataset and obtain scores that do not "
         "reflect real ability.",
         "Hendrycks and Dietterich {c:hendrycks2019} proposed benchmarking robustness by corrupting the inputs at several severity levels, the approach "
         "followed by the noise experiment of this project."])
    H3("Remote Sensing And Software Tools")
    NUM(["Rouse et al. {c:rouse1974} introduced the normalised difference vegetation index, and Tucker {c:tucker1979} showed how red and near-infrared "
         "combinations relate to green vegetation; the satellite tab of the application displays this index.",
         "The scikit-learn library {c:pedregosa2011} and its API design {c:buitinck2013} provide the algorithms and the evaluation tools. NumPy {c:harris2020}, "
         "pandas {c:mckinney2010} and Matplotlib {c:hunter2007} support data handling and plotting.",
         "FastAPI {c:fastapi}, Pydantic {c:pydantic}, Leaflet {c:leaflet} and Esri World Imagery {c:esri} provide the web service, the input validation, the "
         "map and the satellite tiles."])
    H3("Crop And Fertilizer Recommendation Studies")
    NUM(["Pudumalar et al. {c:pudumalar2017} proposed a crop recommendation system for precision agriculture in which several learners "
         "(Random Tree, CHAID, K-Nearest Neighbour and Naive Bayes) are combined by majority voting to recommend a crop for site-specific "
         "soil and climate parameters. The motivation was that farmers often choose crops that do not suit their soil, which lowers productivity.",
         "Kulkarni et al. {c:kulkarni2018} presented an ensemble machine-learning recommender that combines several base models and classifies "
         "soil data into Kharif or Rabi crops. The abstract reports an average accuracy of 99.91% for the combined learners.",
         "Nandom, Abe and Gambo {c:nandom} combined a random forest with hierarchical clustering for crop and fertilizer recommendation and "
         "report an accuracy of 99.70%."])
    P("These studies, like this project, use soil and climate readings and ensemble classifiers, and they report accuracies close to 100%. "
      "Such figures are of the same order as the 99.5% obtained here on the Kaggle crop data. Whether the datasets used in those studies "
      "have the same properties as the Kaggle files was not checked in this project, and the figures above are quoted as reported by the "
      "authors; they were not reproduced.")
    H3("Summary Of The Survey")
    P("The surveyed work treats the algorithms, the evaluation methods and the data-quality problem separately. This project brings them together "
      "for an agricultural recommender: it compares seven classifiers with proper statistical testing, audits the two public datasets, "
      "measures robustness to input noise, and exposes the results through a tested web application.")''']

# ---------- Chapter 3: system analysis (new + tools) ----------
out += ['    H1(3, "System Analysis")']
out += ['''    H2("Functional Requirements")
    P("The system must provide the following functions.")
    BUL(["Accept the soil and weather readings (N, P, K, temperature, humidity, pH, rainfall) and recommend one of 22 crops with a confidence value.",
         "Accept the soil, nutrient and weather readings and recommend one of 7 fertilizers, and warn the user when the model is not reliable.",
         "Show the answers of three models side by side so that the user can compare them.",
         "Produce a soil nutrient audit with corrective actions, a profit estimate, a fertilizer dosage estimate and a crop rotation plan.",
         "Simulate drought, heatwave and heavy-rain conditions and show how the recommended crop changes.",
         "Show a regional satellite view with vegetation, weather and market information, and let the user browse the datasets."])
    H2("Non-Functional Requirements")
    BUL(["Accuracy: the selected crop model must exceed 99% cross-validated accuracy on the benchmark data.",
         "Performance: a prediction must be returned fast enough for interactive use (well below one second).",
         "Reliability: invalid input must be rejected with a clear message, and unreliable models must be flagged.",
         "Usability: all functions are available from one web page with sliders, presets and plain-language results.",
         "Portability: the application must run on any computer with Python, using only open-source software.",
         "Maintainability: the code is organised in a training module, an API module and a static front end, and is covered by automated tests."])
    H2("Hardware Requirements")
    TABLE("Hardware requirements@@tab_hw", ["Component", "Minimum", "Recommended"],
          [["Processor", "Dual-core, 2 GHz", "Quad-core or better"], ["Memory", "4 GB RAM", "8 GB RAM"], ["Storage", "1 GB free", "2 GB free"],
           ["Display", "1280 x 720", "1920 x 1080"], ["Network", "Needed only for map tiles", "Broadband connection"]], widths=[1.8, 2.4, 2.4])
''']
out += sec("Software Requirements", "Technologies And Tools")
out += ['''    H2("Feasibility Study")
    P("Technical feasibility: all required algorithms and libraries are available in open-source Python, the dataset sizes are small enough "
      "for a laptop, and the trained models predict in milliseconds, so the system is technically feasible.")
    P("Economic feasibility: no licensed software or special hardware is needed, and the map tiles and datasets are freely available, so "
      "the development cost is limited to the effort of the team. For a farmer, the cost of use is the time to enter a few readings.")
    P("Operational feasibility: the interface uses sliders, presets and plain-language output, and the application states clearly where "
      "it uses sample data, so a user with basic computer skills can operate it. The main operational risk is the quality of the input "
      "readings, which the system limits by validating ranges.")''']

# ---------- Chapter 4: system design ----------
out += ['    H1(4, "System Design")']
out += sec("System Architecture", "System Architecture")
out += sec("Request Data Flow", "Request Data Flow")
out += sec("Backend Implementation", "Backend Implementation")
out += sec("Web Interface Modules", "Web Interface Modules")
out += sec("Rule-Based Decision Support", "Rule-Based Decision Support")
out += sec("Reliability And Security", "Reliability And Security Considerations")
out += sec("Deployment", "Deployment")

# ---------- Chapter 5: proposed methodology ----------
out += ['    H1(5, "Proposed Methodology")']
out += ['''    P("This chapter describes the proposed methodology: the data preparation, the seven classification algorithms, the evaluation "
      "protocol and the selection of the suitable algorithm. All implementations come from scikit-learn {c:pedregosa2011}.")''']
out += sec("Data Preprocessing", "Data Preprocessing")
out += ['    H2("Classification Algorithms")']
for t, s_ in (("Decision Tree", "Decision Tree"), ("Random Forest", "Random Forest"), ("K-Nearest Neighbours", "K-Nearest Neighbours"),
              ("Support Vector Machine", "Support Vector Machine"), ("Logistic Regression", "Logistic Regression"),
              ("Multilayer Perceptron", "Multilayer Perceptron"), ("Gradient Boosting", "Gradient Boosting")):
    out += sub(t, s_)
out += sec("Performance Metrics", "Performance Metrics")
out += sec("Validation And Statistical Methods", "Validation And Statistical Methods")
out += ['    H2("Selection Of The Suitable Algorithm")']
out += sub("Selection Criteria", "Selection Criteria")
out += sub("Comparative Evaluation", "Comparative Evaluation")
out += sub("Why Random Forest Is Selected", "Why Random Forest Is Selected")

# ---------- Chapter 6: software testing (new) ----------
out += ['    H1(6, "Software Testing")']
out += ['''    P("Testing was carried out at four levels, in the same order as the sample project structure: unit, integration, system and regression.")
    H2("Unit Testing")
    P("Unit testing checks the smallest parts in isolation. The training function fit_and_score was tested on rule-based data to confirm that "
      "it learns when labels carry a signal and reports no warning, and the input schemas were tested with out-of-range and invalid values.")
    H2("Integration Testing")
    P("Integration testing checks that the parts work together. The API tests call the real endpoints through the FastAPI test client, so that the "
      "request validation, the scaler, the models and the response formatting are tested as one chain. In the browser, the shared inputs "
      "of the crop tab and the fertilizer tab were tested to confirm that they stay equal.")
    H2("System Testing")
    P("System testing checks the complete application as a user would use it. Every preset was run through the interface, the sync button "
      "of the soil report was tested after changing an input, and the reliability warning of the fertilizer tab was checked.")
    H2("Regression Testing")
    P("Regression testing repeats the earlier tests after every change, so that new work does not break old behaviour. The six automated "
      "tests are re-run with a single command after each change of the code, and they caught a stale model cache that still held the "
      "old feature list after the fertilizer inputs were changed, which led to a version number in the cache key.")
    H2("Test Cases")
    TABLE("Test cases and their outcomes@@tab_tests", ["ID", "Test description", "Expected result", "Actual result", "Status"],
          [["T01", "Valid crop request (rice example)", "Returns rice and three model answers", "As expected", "Pass"],
           ["T02", "Crop request with pH = 99", "HTTP 422 validation error", "As expected", "Pass"],
           ["T03", "Fertilizer request with unknown soil type", "HTTP 400 with the valid soil list", "As expected", "Pass"],
           ["T04", "Status endpoint, crop data quality", "No warning, accuracy above 90%", "As expected", "Pass"],
           ["T05", "Fertilizer quality flag", "Warning only if best accuracy is within 10 points of chance", "As expected", "Pass"],
           ["T06", "Pipeline on rule-based data", "Accuracy above 80%, no warning", "As expected", "Pass"],
           ["T07", "Change nitrogen in the fertilizer tab", "Crop tab shows the same nitrogen", "As expected", "Pass"],
           ["T08", "Change input, press Sync Live Inputs", "Soil report shows the new values and status", "As expected", "Pass"],
           ["T09", "Load each crop preset", "Rice, chickpea, maize, mothbeans are predicted", "As expected", "Pass"],
           ["T10", "Fertilizer prediction on real data", "Reliability warning is displayed", "As expected", "Pass"]],
          widths=[0.5, 2.1, 2.0, 1.2, 0.7], size=9.5)''']

# ---------- Chapter 7: experimental results ----------
out += ['    H1(7, "Experimental Results")']
for t in ("Experimental Setup", "Exploratory Data Analysis", "Crop Model Results", "Statistical Significance", "Robustness To Sensor Noise",
          "Fertilizer Dataset Analysis", "Rule-Based Synthetic Experiment", "Feature Ablation", "Training And Prediction Time",
          "Application Screenshots", "Discussion"):
    out += sec(t, t)

# ---------- Chapters 8 and 9 ----------
out += ['    H1(8, "Conclusion")']
out += sec("Conclusion", "Conclusion")
out += sec("Learning Outcomes", "Learning Outcomes")
out += ['    H1(9, "Future Enhancement")']
out += sec("Future Scope", "Future Enhancement")

text = "\n".join(head) + "\n\n\ndef chapters():\n" + "\n".join(out) + "\n"
# new reference table data replaces the v1 string REFS (see below)
refs = open("scripts/refs_block.txt", encoding="utf-8").read()
a = text.index("REFS.update({"); b = text.index("\n})\n", a) + 4
text = text[:a] + refs + text[b:]
text = text.replace('"Chapter 4 and Chapter 5.")', '"Chapter 7 and Chapters 8 and 9.")')
open("scripts/report_content.py", "w", encoding="utf-8").write(text)
print("assembled", len(out), "lines;", "unused v1 blocks:", [t for t in blocks if t not in text and not t.startswith("CH:")][:10])
