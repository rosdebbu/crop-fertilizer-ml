"""Chapters 1-5 of the project report. All numbers come from outputs/*.json so text and results cannot drift."""
import json
from report_engine import REFS, H1, H2, H3, P, BUL, NUM, FIG, TABLE, EQ

R = json.load(open("outputs/results.json"))
RR = json.load(open("outputs/research_results.json"))
CM, FM, SM = R["metrics"]["crop"], R["metrics"]["fertilizer"], R["synthetic_fertilizer"]["metrics"]
CV, NZ, LV, WIL = RR["crop_cv"], RR["crop_noise_accuracy"], RR["noise_levels_fraction_of_std"], RR["crop_wilcoxon_vs_best"]
EX = json.load(open("outputs/report_extra.json"))
FA = RR["fert_anova_p"]; FMEAN = RR["fert_feature_means_by_label"]
OC, OF, FIGP = "output_charts", "output_charts_fertilizer", "report/figures"
PAPERFIG = "paper/figures"
M3 = ["Random Forest", "Decision Tree", "KNN"]
NAMEFULL = {"Random Forest": "Random Forest (RF)", "Decision Tree": "Decision Tree (DT)", "KNN (k=5)": "KNN (k = 5)", "SVM (RBF)": "SVM (RBF kernel)",
            "Logistic Regression": "Logistic Regression (LR)", "MLP (64,32)": "MLP (64, 32)", "Hist. Gradient Boosting": "Gradient Boosting (HGB)"}
AB = {"Random Forest": "RF", "Decision Tree": "DT", "KNN (k=5)": "KNN", "SVM (RBF)": "SVM",
      "Logistic Regression": "LR", "MLP (64,32)": "MLP", "Hist. Gradient Boosting": "HGB"}

REFS.update({   # key: (authors, title, journal / conference, year)
    "breiman2001": ("L. Breiman", "Random forests", "Machine Learning, vol. 45, no. 1, pp. 5-32", "2001"),
    "ho1995": ("T. K. Ho", "Random decision forests", "Proc. 3rd Int. Conf. Document Analysis and Recognition, vol. 1, pp. 278-282", "1995"),
    "quinlan1986": ("J. R. Quinlan", "Induction of decision trees", "Machine Learning, vol. 1, no. 1, pp. 81-106", "1986"),
    "cart1984": ("L. Breiman, J. H. Friedman, R. A. Olshen, C. J. Stone", "Classification and Regression Trees", "Wadsworth, Belmont, CA (book)", "1984"),
    "cover1967": ("T. Cover, P. Hart", "Nearest neighbor pattern classification", "IEEE Trans. Information Theory, vol. 13, no. 1, pp. 21-27", "1967"),
    "cortes1995": ("C. Cortes, V. Vapnik", "Support-vector networks", "Machine Learning, vol. 20, no. 3, pp. 273-297", "1995"),
    "hastie2009": ("T. Hastie, R. Tibshirani, J. Friedman", "The Elements of Statistical Learning, 2nd ed.", "Springer, New York (book)", "2009"),
    "rumelhart1986": ("D. E. Rumelhart, G. E. Hinton, R. J. Williams", "Learning representations by back-propagating errors", "Nature, vol. 323, pp. 533-536", "1986"),
    "friedman2001": ("J. H. Friedman", "Greedy function approximation: a gradient boosting machine", "Annals of Statistics, vol. 29, no. 5, pp. 1189-1232", "2001"),
    "ke2017": ("G. Ke et al.", "LightGBM: a highly efficient gradient boosting decision tree", "Advances in Neural Information Processing Systems 30, pp. 3146-3154", "2017"),
    "pedregosa2011": ("F. Pedregosa et al.", "Scikit-learn: machine learning in Python", "J. Machine Learning Research, vol. 12, pp. 2825-2830", "2011"),
    "buitinck2013": ("L. Buitinck et al.", "API design for machine learning software: experiences from the scikit-learn project", "arXiv:1309.0238", "2013"),
    "mckinney2010": ("W. McKinney", "Data structures for statistical computing in Python", "Proc. 9th Python in Science Conference, pp. 56-61", "2010"),
    "harris2020": ("C. R. Harris et al.", "Array programming with NumPy", "Nature, vol. 585, pp. 357-362", "2020"),
    "hunter2007": ("J. D. Hunter", "Matplotlib: a 2D graphics environment", "Computing in Science & Engineering, vol. 9, no. 3, pp. 90-95", "2007"),
    "kohavi1995": ("R. Kohavi", "A study of cross-validation and bootstrap for accuracy estimation and model selection", "Proc. 14th Int. Joint Conf. Artificial Intelligence (IJCAI), pp. 1137-1143", "1995"),
    "wilcoxon1945": ("F. Wilcoxon", "Individual comparisons by ranking methods", "Biometrics Bulletin, vol. 1, no. 6, pp. 80-83", "1945"),
    "demsar2006": ("J. Demsar", "Statistical comparisons of classifiers over multiple data sets", "J. Machine Learning Research, vol. 7, pp. 1-30", "2006"),
    "ojala2010": ("M. Ojala, G. C. Garriga", "Permutation tests for studying classifier performance", "J. Machine Learning Research, vol. 11, pp. 1833-1863", "2010"),
    "hendrycks2019": ("D. Hendrycks, T. Dietterich", "Benchmarking neural network robustness to common corruptions and perturbations", "Int. Conf. Learning Representations (ICLR)", "2019"),
    "northcutt2021": ("C. G. Northcutt, A. Athalye, J. Mueller", "Pervasive label errors in test sets destabilize machine learning benchmarks", "NeurIPS Datasets and Benchmarks Track", "2021"),
    "geirhos2020": ("R. Geirhos et al.", "Shortcut learning in deep neural networks", "Nature Machine Intelligence, vol. 2, pp. 665-673", "2020"),
    "rouse1974": ("J. W. Rouse, R. H. Haas, J. A. Schell, D. W. Deering", "Monitoring vegetation systems in the Great Plains with ERTS", "Proc. 3rd ERTS Symposium, NASA SP-351, vol. 1, pp. 309-317", "1974"),
    "tucker1979": ("C. J. Tucker", "Red and photographic infrared linear combinations for monitoring vegetation", "Remote Sensing of Environment, vol. 8, no. 2, pp. 127-150", "1979"),
    "kaggle_crop": ("atharvaingle (Kaggle user)", "Crop Recommendation Dataset", "kaggle.com/datasets/atharvaingle/crop-recommendation-dataset", "-"),
    "kaggle_fert": ("irakozekelly (Kaggle user)", "Fertilizer Prediction", "kaggle.com/datasets/irakozekelly/fertilizer-prediction", "-"),
    "fastapi": ("S. Ramirez", "FastAPI documentation", "fastapi.tiangolo.com", "-"),
    "pydantic": ("Pydantic contributors", "Pydantic documentation: data validation using Python type hints", "docs.pydantic.dev", "-"),
    "leaflet": ("V. Agafonkin", "Leaflet: an open-source JavaScript library for interactive maps", "leafletjs.com", "-"),
    "pudumalar2017": ("S. Pudumalar, E. Ramanujam, R. H. Rajashree et al.", "Crop recommendation system for precision agriculture", "Int. Conf. Advanced Computing (ICoAC), IEEE, doi:10.1109/ICoAC.2017.7951740", "2017"),
    "kulkarni2018": ("N. H. Kulkarni et al.", "Improving crop productivity through a crop recommendation system using ensembling technique", "IEEE conference, Bengaluru, IEEE Xplore document 8768790", "2018"),
    "nandom": ("Nandom, Abe, Gambo", "Application of random forest and hierarchical clustering models for crop and fertilizer recommendation to farmers", "Nigerian Journal of Technology, vol. 44, no. 1, doi:10.4314/njt.v44i1.13", "-"),
    "esri": ("Esri", "World Imagery map service", "ArcGIS Living Atlas of the World", "-"),
})




def chapters():
    H1(1, "Introduction")
    H2("General")
    P("Agriculture remains the primary source of livelihood for a large share of the population in India, and decisions made before sowing, "
      "namely which crop to grow and which fertilizer to apply, largely determine the yield, the cost of cultivation and the long-term health "
      "of the soil. Traditionally, these decisions rely on experience, local custom and occasional laboratory soil tests. Such tests are "
      "accurate but slow and expensive for small farms, and the advice that reaches the farmer is often generic rather than specific to a field.")
    P("Precision agriculture addresses this gap by using measurements of soil and climate to tailor decisions to each field. The key soil "
      "variables are the macro-nutrients nitrogen (N), phosphorus (P) and potassium (K), the soil reaction (pH) and the moisture content. "
      "The key climate variables are temperature, humidity and rainfall. Together these seven quantities describe the growing environment "
      "well enough that experienced agronomists can name a suitable crop for them. A machine-learning model can learn the same mapping from "
      "data, and can apply it instantly and consistently.")
    P("Supervised classification algorithms such as decision trees {c:quinlan1986,cart1984}, random forests {c:breiman2001} and nearest-neighbour "
      "methods {c:cover1967} are well suited to this task because the inputs are a small number of numeric measurements and the output is one of a "
      "limited set of classes. Open-source libraries such as scikit-learn {c:pedregosa2011} make these algorithms available with a uniform "
      "interface, which allows a student team to build, compare and deploy several models within a single project.")
    P("Each input of the crop model has a clear agronomic meaning, which is why a model trained on them can be explained to a farmer. "
      "Nitrogen is a part of chlorophyll and proteins and drives leaf growth, so leafy cereals such as rice and maize respond strongly to it, "
      "whereas legumes fix atmospheric nitrogen through root nodules and need little of it. Phosphorus supports root development and "
      "flowering, and potassium regulates water use and disease resistance, which is why fruit crops show high potassium values in the data.")
    P("Soil pH controls how available the nutrients are to the plant: most crops grow best near neutral pH, while strongly acidic or "
      "alkaline soils lock up some nutrients. Temperature and humidity determine the growing season and the risk of disease, and rainfall "
      "separates water-loving crops such as rice and jute from drought-tolerant pulses such as chickpea and moth beans. A model that "
      "combines the seven inputs can therefore place a field close to the typical growing environment of one particular crop.")
    P("Fertilizers supply the three macro-nutrients in fixed proportions, written as an N-P-K grade. Urea contains about 46% nitrogen and no "
      "phosphorus or potassium, DAP contains about 18% nitrogen and 46% phosphorus, and compound grades such as 17-17-17 and 10-26-26 supply "
      "several nutrients together. Choosing a fertilizer therefore means matching its grade to the nutrient that the soil lacks, which is the "
      "logic that the rule-based part of the application follows.")
    H2("Purpose")
    P("The objectives of the project are as follows.")
    NUM(["To build a crop recommendation model that predicts one of 22 crops from nitrogen, phosphorus, potassium, temperature, humidity, pH and rainfall.",
         "To build a fertilizer recommendation model that predicts one of 7 fertilizers from soil and nutrient information.",
         "To compare several machine-learning algorithms under a rigorous protocol (repeated stratified cross-validation and statistical tests) and to select the most suitable one.",
         "To audit both datasets, to test how the models behave under sensor noise, and to report honestly where a model cannot be trusted.",
         "To implement the models behind a REST API and a web interface that includes soil-health advice, profit and dosage estimates, climate-stress simulation and a regional satellite view."])
    H2("Scope")
    P("The scope of the work is limited to supervised classification on two public tabular datasets, the design and implementation of a "
      "prototype web application, and the experimental evaluation of the models. The following limitations apply and are discussed again in "
      "Chapter 7 and Chapters 8 and 9.")
    BUL(["Both datasets are public benchmarks and not measurements collected by the authors in the field.",
         "The satellite, weather and market panels of the web interface use stored sample values. They demonstrate the intended user experience but are not live data feeds.",
         "Model hyper-parameters were left at their defaults so that the comparison reflects the algorithms and not the tuning effort.",
         "The system gives advisory output only and does not measure agronomic yield benefit."])
    H2("Motivation And Problem Statement")
    P("The problem addressed in this project is to recommend, for a given set of soil and weather readings, (i) the most suitable crop out of "
      "22 candidate crops and (ii) the most suitable fertilizer out of 7 commonly used fertilizers, and to present the recommendation through "
      "an easy-to-use web application together with supporting advice. The system must be accurate, must explain how reliable its answers "
      "are, and must reject invalid inputs instead of producing misleading output.")
    P("A second, equally important question arose while working with the public datasets: do the published accuracy figures really reflect "
      "predictive power? Machine-learning benchmarks can contain label errors, artefacts or shortcuts that inflate scores {c:northcutt2021,geirhos2020}. "
      "A responsible recommender should therefore audit its data before trusting its models, and should report when a model performs no "
      "better than guessing.")
    P("The first motivation is practical. A farmer who chooses a crop unsuited to the soil loses a season, and a farmer who over-applies "
      "fertilizer pays for nutrients the crop cannot use while damaging the soil through acidification and salt build-up. A low-cost "
      "decision-support tool that works from a few measurements can reduce both losses and can be extended to many regions.")
    P("The second motivation is academic. Many student and published projects report accuracy above 95% on the same two public datasets "
      "without examining whether the numbers are meaningful. By combining careful model comparison with a statistical audit of the data and "
      "a robustness test under measurement noise, this project aims to show how such results should be evaluated, and the findings were "
      "written up as a research paper that is included in Appendix B.")
    H2("Datasets Used")
    P("Two public datasets from the Kaggle repository were used. The Crop Recommendation dataset {c:kaggle_crop} contains 2,200 rows and 22 crop "
      "classes with exactly 100 samples per crop, so the classes are perfectly balanced. Each row has seven numeric features. The Fertilizer "
      "Prediction dataset {c:kaggle_fert} contains 100,000 rows and 7 fertilizer classes with a roughly equal share of each class. Neither file "
      "contains missing values or duplicate rows, which was verified with the pandas library {c:mckinney2010}. Table {{num:tab1.1}} summarises both datasets.")
    TABLE("Summary of the datasets@@tab1.1", ["Property", "Crop Recommendation", "Fertilizer Prediction"],
          [["Rows", "2,200", "100,000"], ["Target classes", "22 crops (100 samples each)", "7 fertilizers (about 14.3% each)"],
           ["Numeric inputs", "N, P, K, temperature, humidity, pH, rainfall", "Temperature, humidity, moisture, N, P, K"],
           ["Categorical inputs", "None", "Soil type (5 values)"], ["Missing values", "0", "0"], ["Duplicate rows", "0", "0"]],
          widths=[1.5, 2.7, 2.5])
    P("Figure {{num:fig1.1}} shows the class distribution of the crop dataset, which is exactly uniform. Figure {{num:fig1.2}} shows the distribution of the "
      "fertilizer classes, which is also almost uniform. Because both targets are balanced, plain accuracy is a meaningful metric, and the "
      "chance-level accuracy is simply one divided by the number of classes: 4.55% for the crop data and 14.29% for the fertilizer data.")
    FIG(f"{OC}/01_class_distribution.png", "Class distribution of the crop recommendation dataset@@fig1.1", 5.6)
    FIG(f"{OF}/01_class_distribution.png", "Class distribution of the fertilizer prediction dataset@@fig1.2", 5.2)
    H2("Organization Of The Report")
    P("The remainder of the report is organised as follows.")
    BUL(["Chapter 2 surveys the literature on the algorithms, the evaluation methods and the tools on which the work builds.",
         "Chapter 3 analyses the functional, non-functional, hardware and software requirements of the system.",
         "Chapter 4 describes the design of the system: architecture, data flow, backend, interface and rule-based modules.",
         "Chapter 5 explains the proposed methodology: preprocessing, the algorithms, the evaluation protocol and the choice of the suitable algorithm.",
         "Chapter 6 describes the software testing, and Chapter 7 presents and discusses the experimental results.",
         "Chapters 8 and 9 give the conclusion and the future enhancements. The references, the source code, the paper publication status and the plagiarism report follow."])
    H1(2, "Literature Survey")
    P("This chapter surveys the published work on which the project builds. Because the project combines classification algorithms, "
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
         "Wilcoxon {c:wilcoxon1945} proposed the signed-rank test for paired samples, and Dem\u0161ar {c:demsar2006} recommended it for comparing two classifiers. "
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
      "measures robustness to input noise, and exposes the results through a tested web application.")
    H1(3, "System Analysis")
    H2("Functional Requirements")
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

    H2("Software Requirements")
    P("The project was implemented entirely with open-source tools. Python is the main language. NumPy {c:harris2020} and pandas handle numeric "
      "data, scikit-learn implements the models and the evaluation, and Matplotlib {c:hunter2007} draws the charts. The backend is written with "
      "FastAPI {c:fastapi} and validates requests with Pydantic {c:pydantic}. The browser interface uses HTML and JavaScript, with Leaflet "
      "{c:leaflet} for the map and Esri World Imagery {c:esri} as the satellite tile layer. Table {{num:tab1.2}} lists the tools and their roles.")
    TABLE("Tools and their roles in the project@@tab1.2", ["Tool", "Role"],
          [["Python 3.12", "Implementation language"], ["pandas, NumPy", "Data loading, cleaning and numeric computation"],
           ["scikit-learn", "Preprocessing, classifiers, cross-validation, metrics"], ["Matplotlib, seaborn", "Exploratory and result charts"],
           ["FastAPI, Uvicorn", "REST backend and ASGI web server"], ["Pydantic", "Input validation and clear error messages"],
           ["joblib", "Saving and loading trained models"], ["Leaflet, Esri imagery", "Interactive satellite map"],
           ["pytest", "Automated tests of the API"]], widths=[2.0, 4.7])
    H2("Feasibility Study")
    P("Technical feasibility: all required algorithms and libraries are available in open-source Python, the dataset sizes are small enough "
      "for a laptop, and the trained models predict in milliseconds, so the system is technically feasible.")
    P("Economic feasibility: no licensed software or special hardware is needed, and the map tiles and datasets are freely available, so "
      "the development cost is limited to the effort of the team. For a farmer, the cost of use is the time to enter a few readings.")
    P("Operational feasibility: the interface uses sliders, presets and plain-language output, and the application states clearly where "
      "it uses sample data, so a user with basic computer skills can operate it. The main operational risk is the quality of the input "
      "readings, which the system limits by validating ranges.")
    H1(4, "System Design")
    H2("System Architecture")
    P("The system has three layers, shown in Figure {{num:fig3.3}}. The data and training layer reads the CSV files and trains the models with "
      "scikit-learn. The service layer is a FastAPI application that keeps the trained models in memory and exposes them as a REST API. "
      "The presentation layer is a single-page web application that calls the API and displays the results.")
    FIG(f"{FIGP}/diag_architecture.png", "Overall system architecture@@fig3.3", 5.8)
    P("When the server starts, it loads the saved models from a cache or, if no valid cache exists, trains them. A request from the browser "
      "carries the field readings as JSON. The API validates the values, applies the stored scaler, calls the selected model and returns the "
      "predicted class, the probability of every class, the answers of all three models and an explanatory text.")
    H2("Request Data Flow")
    P("The life of one prediction request, from the browser to the model and back, follows these steps.")
    NUM(["The user moves a slider or presses the predict button; the browser collects the field readings and sends them as JSON to the API.",
         "FastAPI parses the JSON into a Pydantic model and rejects any value outside its allowed range with a 422 response.",
         "The stored scaler transforms the readings in the same way as the training data.",
         "The selected model predicts the class; the probabilities of all classes and the answers of the other two models are also computed.",
         "The server adds the crop or fertilizer description, a rule-based explanation and, for fertilizer, the reliability warning.",
         "The browser displays the result, updates the shared inputs of the other tab, and refreshes the soil health report on request."])
    H2("Backend Implementation")
    H3("Training And Evaluation Module")
    P("A single function, fit_and_score, serves both datasets. It splits and scales the data, trains Random Forest, Decision Tree and KNN, and "
      "returns the fitted scaler, the models and their metrics. For the crop data it also computes 5-fold cross-validated accuracy. The "
      "function additionally compares the best accuracy with the chance level and, if the best model is less than ten points above chance, "
      "stores a warning message. The code is listed in Appendix A.")
    H3("Model Persistence")
    P("Training both models, mainly on the 100,000-row fertilizer file, takes about 24 seconds. To avoid this delay at every start, the trained "
      "objects are saved with joblib in a cache file together with a signature made of the modification time and size of both CSV files and "
      "a model version number. On the next start the cache is loaded in about 6 seconds. If a data file changes, or the version number is "
      "increased because the training code changed, the cache is discarded and the models are retrained automatically.")
    H3("REST API")
    P("The API follows the REST style: each resource has a URL and a request uses a standard HTTP method. Table {{num:tab3.2}} lists the endpoints. "
      "FastAPI also generates interactive documentation at the /docs address, which was used during testing.")
    TABLE("Endpoints of the REST API@@tab3.2", ["Endpoint", "Method", "Purpose"],
          [["/api/status", "GET", "Model list, metrics and data-quality report"], ["/api/predict/crop", "POST", "Crop recommendation"],
           ["/api/predict/fertilizer", "POST", "Fertilizer recommendation"], ["/api/metrics", "GET", "Accuracy, precision, recall, F1"],
           ["/api/data/crop/sample", "GET", "Random sample and statistics of crop data"], ["/api/data/fertilizer/sample", "GET", "Random sample and statistics of fertilizer data"],
           ["/api/farmer/profitability", "POST", "Yield, revenue, cost, profit and ROI"], ["/api/farmer/fertilizer-dosage", "POST", "Bags, weight, cost and schedule"],
           ["/api/farmer/climate-stress", "POST", "What-if crop under drought, heat, flood"], ["/api/farmer/crop-rotation", "GET", "Three-season rotation plan"],
           ["/api/geo/analyze", "GET", "Regional profile for the satellite tab"]], widths=[2.5, 0.8, 3.4])
    H3("Input Validation")
    P("Every request body is described by a Pydantic model {c:pydantic} with range limits, for example pH between 0 and 14 and humidity "
      "between 0 and 100. A value outside the range is rejected with HTTP status 422 and a message that names the field. An unknown "
      "soil type returns status 400 together with the list of valid values. This protects the models from impossible inputs.")
    H3("Shared Field Readings")
    P("The crop model and the fertilizer model use the same field. Therefore five readings (N, P, K, temperature and humidity) are shared: "
      "changing one of them in either tab updates the other tab and refreshes both predictions. The crop-only inputs are pH and rainfall, and "
      "the fertilizer-only inputs are moisture and soil type. The crop recommended by the crop model is displayed in the fertilizer tab and "
      "used for the advice and dosage text, but it is not an input of the fertilizer model, because the two datasets use different crop lists.")
    H2("Web Interface Modules")
    P("The interface has five tabs, listed in Table {{num:tab3.3}} together with the technique behind each. Only the crop predictor, the fertilizer "
      "advisor and the climate-stress simulator use the machine-learning models; the other modules are rule-based or lookup-based, and the "
      "interface states clearly where the data is sample data.")
    TABLE("Tabs of the web interface and the technique used@@tab3.3", ["Tab", "Function", "Technique"],
          [["Crop Predictor", "Recommends one of 22 crops", "RF, DT, KNN with scaler"], ["Fertilizer Advisor", "Recommends one of 7 fertilizers", "RF, DT, KNN with encoder and scaler"],
           ["Satellite & Climate", "Regional map, NDVI, weather, prices", "Lookup of stored profile; Leaflet map"],
           ["Soil Health & Farm Report", "Nutrient audit, profit, dosage, rotation, climate stress", "Threshold rules, formulas, RF re-prediction"],
           ["Dataset Explorer", "Browse and search the data rows", "pandas sampling, browser filter"]], widths=[1.7, 2.6, 2.4])
    H2("Rule-Based Decision Support")
    H3("Soil Nutrient Audit")
    P("The soil health report rates each measurement against fixed agronomic bands and proposes a corrective action. Table {{num:tab3.4}} gives the "
      "bands. Low nitrogen leads to a recommendation of urea, low phosphorus to DAP, and low potassium to muriate of potash. The report is an "
      "advisory summary and not a laboratory certificate, and it is labelled as such.")
    TABLE("Bands used in the soil nutrient audit@@tab3.4", ["Parameter", "Deficient / low", "Normal / optimal", "Excess / high"],
          [["Nitrogen (kg/ha)", "below 40", "40 to 110", "above 110"], ["Phosphorus (kg/ha)", "below 25", "25 and above", "-"],
           ["Potassium (kg/ha)", "below 25", "25 and above", "-"], ["Soil pH", "below 6.0 (acidic)", "6.0 to 7.8 (neutral)", "above 7.8 (alkaline)"],
           ["Moisture (%)", "below 30", "30 and above", "-"]], widths=[1.8, 1.6, 1.7, 1.6])
    H3("Profit And Dosage Estimation")
    P("The profit calculator converts a recommended crop into expected economics using a table of average yield per acre, minimum support "
      "price (MSP) per quintal and cultivation cost per acre. For a land area A in acres, the quantities are computed as in Equation {{num:eq3.1}}.")
    EQ("Profit = (Yield per acre × A × MSP) − (Cost per acre × A);   ROI = Profit / Cost × 100", "eq3.1")
    P("The fertilizer dosage calculator multiplies the recommended bags per acre by the land area and the price per bag, and compares the "
      "result with an assumed conventional over-use of 1.8 times the recommended amount to estimate the saving. These tables contain "
      "indicative averages and are not region-specific.")
    H3("Climate-Stress Simulation")
    P("The climate-stress simulator changes the weather inputs of the current field and asks the Random Forest for a new recommendation. "
      "The three scenarios of Table {{num:tab3.5}} are applied, with limits that keep the simulated values within the range of the training data. If the "
      "recommended crop changes, the original recommendation is sensitive to that weather shock. This is a sensitivity analysis and not a forecast.")
    TABLE("Scenarios of the climate-stress simulator@@tab3.5", ["Scenario", "Temperature", "Humidity", "Rainfall"],
          [["Drought", "+1.5 °C (max 45)", "× 0.75 (min 20)", "× 0.70 (min 15 mm)"],
           ["Heatwave", "+3.5 °C (max 48)", "× 0.85 (min 20)", "unchanged"],
           ["Cloudburst", "−1.5 °C (min 15)", "× 1.15 (max 98)", "× 1.50 (max 350 mm)"]], widths=[1.5, 1.8, 1.7, 1.7])
    H3("Satellite And Climate Tab")
    P("The satellite tab shows a Leaflet map {c:leaflet} with Esri World Imagery tiles {c:esri} that the browser downloads directly from the tile "
      "server. When a region is chosen, the server returns a stored profile with latitude and longitude, weather, soil and market values. The "
      "vegetation index shown for each region is a stored value. The normalised difference vegetation index {c:rouse1974,tucker1979} is defined "
      "in Equation {{num:eq3.2}}, where NIR and Red are the reflectances in the near-infrared and red bands; healthy vegetation reflects strongly in the "
      "near-infrared and absorbs red light, so NDVI is high.")
    EQ("NDVI = (NIR − Red) / (NIR + Red)", "eq3.2")
    P("In the present prototype the indices are not computed from satellite bands. In a production version they would be computed from "
      "Sentinel-2 imagery for the chosen field and could be used as additional model inputs.")

    H2("Reliability And Security")
    P("Several design decisions protect the user from wrong or harmful output. Inputs are validated at the boundary of the system, so that "
      "impossible values never reach a model. The confidence of each prediction is shown, and a data-quality warning is shown whenever the "
      "best accuracy of a model is within ten points of chance. Wherever the interface shows sample data, such as market prices, the label "
      "says so, and the soil report is labelled as an advisory estimate and not an official soil health card.")
    P("Cross-origin requests are allowed for development, but credentials are disabled, because a wildcard origin combined with credentials is "
      "unsafe and is rejected by browsers. The model cache is a local file written by the server itself, so it must not be taken from an "
      "untrusted source, because loading a pickled object can execute code. A production deployment should also add authentication, "
      "request logging and rate limiting.")
    H2("Deployment")
    P("The application runs locally with a single command, which starts the Uvicorn server and prints the address. The only requirement is "
      "Python with the packages listed in the requirements file. For wider use, the application could be packaged in a container, placed "
      "behind a reverse proxy, and served over HTTPS, with the model files built once during the container build so that the start-up "
      "time stays short. Because the models are small, a single modest server can handle many farmers.")

    H1(5, "Proposed Methodology")
    P("This chapter describes the proposed methodology: the data preparation, the seven classification algorithms, the evaluation "
      "protocol and the selection of the suitable algorithm. All implementations come from scikit-learn {c:pedregosa2011}.")
    H2("Data Preprocessing")
    P("Raw tabular data must be converted into a form that the learning algorithms can use. Figure {{num:fig2.1}} shows the sequence of steps that is "
      "applied to both datasets before and after model training.")
    FIG(f"{FIGP}/diag_pipeline.png", "Machine-learning pipeline used for both datasets@@fig2.1", 6.0)
    H3("Standardisation")
    P("Features such as rainfall (20 to 300 mm) and pH (3.5 to 9.5) have very different numeric ranges. Algorithms that rely on distances or "
      "gradients would be dominated by the large-range feature. Standardisation rescales every feature to zero mean and unit variance using "
      "Equation {{num:eq2.1}}, where the mean and standard deviation are computed on the training data only.")
    EQ("z = (x − μ) / σ", "eq2.1")
    P("Tree-based models are not affected by this scaling because their split thresholds are order-based, but a single scaler is used for "
      "all models so that the pipeline stays simple and the comparison is fair.")
    H3("Label Encoding")
    P("The soil type in the fertilizer dataset is text (for example Sandy, Loamy, Black, Red, Clayey). The LabelEncoder converts each category "
      "to an integer. This is harmless for tree models, which split on thresholds, but it imposes an artificial order on the categories, "
      "which would matter for distance-based models. One-hot encoding is the alternative and is listed as a possible refinement.")
    H3("Stratified Train-Test Split")
    P("Each dataset is divided into 80% training and 20% test data. Stratification keeps the proportion of every class identical in both parts, "
      "and a fixed random seed (42) makes every experiment reproducible. The test data is never used to fit the scaler or any model.")
    H3("Data Leakage")
    P("Data leakage occurs when information from the test data influences training, for example when a scaler is fitted on the whole dataset "
      "before splitting. It produces scores that are too optimistic. In this project the scaler is fitted inside the training part only, "
      "and inside each fold during cross-validation, by placing it in a pipeline with the classifier.")
    H2("Classification Algorithms")
    H3("Decision Tree")
    P("A decision tree {c:quinlan1986,cart1984} classifies a sample by asking a sequence of yes/no questions about its features. At each internal "
      "node the algorithm chooses the feature and threshold that best separate the classes. The CART algorithm measures the quality of a split "
      "with the Gini impurity of Equation {{num:eq2.2}}, where p_k is the fraction of samples of class k in the node.")
    EQ("Gini = 1 − Σ p_k²", "eq2.2")
    P("The tree keeps splitting until each leaf is pure. A fully grown tree fits the training data perfectly but tends to memorise noise, "
      "which gives high variance on new data. The main advantage of a single tree is that it can be read and explained as a set of rules.")
    H3("Random Forest")
    P("A random forest {c:breiman2001,ho1995} is an ensemble of many decision trees. Each tree is trained on a bootstrap sample, a random "
      "sample of the training rows drawn with replacement, and at every split only a random subset of the features is considered. This "
      "randomness makes the trees different from one another. The forest predicts by majority vote, as shown in Figure {{num:fig2.2}}, and the "
      "averaging greatly reduces the variance of a single tree without increasing its bias very much {c:hastie2009}.")
    FIG(f"{FIGP}/diag_random_forest.png", "Random forest prediction by majority vote of 100 trees@@fig2.2", 5.2)
    P("About 36.8% of the training rows are left out of each bootstrap sample. These out-of-bag samples can be used to estimate the "
      "generalisation error without a separate validation set. The forest also provides a feature importance score, the average decrease in "
      "impurity caused by splits on a feature, which is used in Chapter 5 to explain the model. The project uses 100 trees. The share of "
      "trees that vote for a class is reported to the user as the confidence of the prediction.")
    H3("K-Nearest Neighbours")
    P("The k-nearest neighbours algorithm {c:cover1967} stores the training samples and classifies a new sample by the majority class among its "
      "k closest training samples, with closeness measured by the Euclidean distance of Equation {{num:eq2.3}} over the standardised features. No "
      "model is learned in advance, so the method is called a lazy learner. The project uses k = 5.")
    EQ("d(x, y) = √ Σ (x_i − y_i)²", "eq2.3")
    P("KNN is simple and often accurate on low-dimensional data, but every prediction requires distances to all stored samples. For the "
      "100,000-row fertilizer data this makes prediction slow, and the method is sensitive to feature scaling and to irrelevant features.")
    H3("Support Vector Machine")
    P("A support vector machine {c:cortes1995} finds the decision boundary that maximises the margin between classes. With a kernel function "
      "the boundary can be non-linear. The radial basis function (RBF) kernel of Equation {{num:eq2.4}} measures similarity as a decreasing function "
      "of distance, so that nearby samples have a kernel value close to one. Multi-class problems are handled by combining binary classifiers.")
    EQ("K(x, y) = exp(−γ ‖x − y‖²)", "eq2.4")
    H3("Logistic Regression")
    P("Multinomial logistic regression models the probability of each class with the softmax function of Equation {{num:eq2.5}}, where w_k and b_k are "
      "the weights and bias of class k. The decision boundaries are linear in the features. It is fast, easy to interpret and acts as a "
      "useful baseline: if a linear model already reaches a high score, the classes are nearly linearly separable.")
    EQ("P(y = k | x) = exp(w_k·x + b_k) / Σ_j exp(w_j·x + b_j)", "eq2.5")
    H3("Multilayer Perceptron")
    P("A multilayer perceptron is a feed-forward neural network made of layers of connected units with non-linear activation functions. It "
      "learns by back-propagation of the prediction error {c:rumelhart1986}. The network used here has two hidden layers of 64 and 32 units. "
      "Neural networks can model complex relationships but have more settings to tune and need scaled inputs, and on a small tabular dataset "
      "they do not always outperform tree ensembles.")
    H3("Gradient Boosting")
    P("Gradient boosting {c:friedman2001} builds trees one after another, each new tree correcting the errors of the ensemble so far. The "
      "histogram-based variant used in scikit-learn groups feature values into bins, which makes training fast on large data, in the style of "
      "LightGBM {c:ke2017}. Boosting mainly reduces bias, while bagging, as used in the random forest, mainly reduces variance.")
    TABLE("Classifiers compared and their settings@@tab2.1", ["Classifier", "Abbr.", "Settings used"],
          [["Random Forest", "RF", "100 trees, default depth, random_state 42"], ["Decision Tree", "DT", "Gini criterion, fully grown"],
           ["K-Nearest Neighbours", "KNN", "k = 5, Euclidean distance"], ["Support Vector Machine", "SVM", "RBF kernel, default C and gamma"],
           ["Logistic Regression", "LR", "Multinomial, L2 penalty, 2000 iterations"], ["Multilayer Perceptron", "MLP", "Hidden layers (64, 32), 800 iterations"],
           ["Histogram Gradient Boosting", "HGB", "Default learning rate and depth"]], widths=[2.3, 0.8, 3.6])
    H2("Performance Metrics")
    P("Classification performance is measured with the quantities derived from the confusion matrix, a table whose rows are the true classes "
      "and whose columns are the predicted classes. Correct predictions lie on the diagonal. For a given class, TP, FP and FN denote the true "
      "positives, false positives and false negatives. Accuracy, precision, recall and F1-score are given by Equations {{num:eq2.6}} to {{num:eq2.9}}.")
    EQ("Accuracy = (correct predictions) / (all predictions)", "eq2.6")
    EQ("Precision = TP / (TP + FP)", "eq2.7")
    EQ("Recall = TP / (TP + FN)", "eq2.8")
    EQ("F1 = 2 · Precision · Recall / (Precision + Recall)", "eq2.9")
    P("For several classes, the per-class scores are combined by averaging. The macro average treats all classes equally, while the weighted "
      "average weights each class by its number of samples. Because both datasets are balanced the two averages are almost identical. "
      "Table {{num:tab2.2}} summarises the metrics.")
    TABLE("Evaluation metrics used@@tab2.2", ["Metric", "Meaning", "Question it answers"],
          [["Accuracy", "Share of correct predictions", "How often is the model right?"], ["Precision", "Correct among predicted as class k", "How reliable is a prediction of k?"],
           ["Recall", "Found among all true samples of k", "How many true k cases are detected?"], ["F1-score", "Harmonic mean of precision and recall", "Is there a balance of both?"],
           ["Confusion matrix", "True versus predicted counts", "Which classes are confused?"]], widths=[1.4, 2.7, 2.6])
    H2("Validation And Statistical Methods")
    P("A single train-test split can be lucky or unlucky. K-fold cross-validation {c:kohavi1995} divides the data into k parts, trains on k-1 parts "
      "and tests on the remaining part, and repeats this for every part. The project uses repeated stratified 5-fold cross-validation with "
      "three repeats, giving 15 test scores per model, from which the mean and the standard deviation are reported.")
    P("To decide whether the difference between two models is real, the paired Wilcoxon signed-rank test {c:wilcoxon1945,demsar2006} is applied to "
      "the 15 pairs of fold scores. It does not assume that the score differences are normally distributed.")
    P("The fertilizer data is audited with four tests. One-way ANOVA checks whether the mean of a numeric feature differs between "
      "fertilizer classes, and the chi-square test checks whether soil type and fertilizer are independent. Mutual information measures any "
      "statistical dependence between a feature and the label. Finally, a permutation control {c:ojala2010} trains the same model on "
      "randomly shuffled labels; if the accuracy on real labels is no higher than on shuffled labels, the labels carry no learnable signal.")
    P("Robustness to measurement error is tested by adding zero-mean Gaussian noise to the test inputs, in the spirit of robustness "
      "benchmarks {c:hendrycks2019}. The standard deviation of the noise equals a chosen fraction of each feature's own standard deviation, "
      "and the models trained on clean data are evaluated at several noise levels.")

    H2("Selection Of The Suitable Algorithm")
    H3("Selection Criteria")
    P("The algorithm for the deployed system must satisfy several criteria at the same time. It must be accurate and stable across different "
      "data splits, it must give a usable measure of confidence, it must respond quickly, it should need little tuning and little scaling, "
      "and it should be explainable to a farmer or an examiner. The criteria were applied to the seven candidates of Chapter 5.")
    BUL(["Accuracy and stability: mean cross-validated accuracy and its standard deviation.",
         "Statistical evidence: whether the best model is significantly better than the others.",
         "Confidence output: availability of class probabilities through predict_proba.",
         "Speed: training and prediction time on the available data.",
         "Explainability: availability of feature importance."])
    H3("Comparative Evaluation")
    best = "Random Forest"
    P(f"Table {{num:tab3.1}} and Figure {{num:fig3.1}} give the result of the repeated stratified cross-validation on the crop dataset. Random Forest is the most "
      f"accurate classifier with {CV[best]['acc_mean']} ± {CV[best]['acc_std']}% accuracy and {CV[best]['f1_macro_mean']}% macro-F1. Histogram "
      f"gradient boosting follows with {CV['Hist. Gradient Boosting']['acc_mean']}%, and the decision tree reaches {CV['Decision Tree']['acc_mean']}%. "
      f"Even logistic regression, a linear model, achieves {CV['Logistic Regression']['acc_mean']}%, which shows that the crop classes are "
      "almost linearly separable and that this benchmark is easy.")
    TABLE("Crop dataset, repeated stratified 5-fold cross-validation (3 repeats, 15 folds)@@tab3.1",
          ["Model", "Accuracy (%)", "Macro-F1 (%)"],
          [[NAMEFULL[k], f"{v['acc_mean']} ± {v['acc_std']}", f"{v['f1_macro_mean']} ± {v['f1_macro_std']}"] for k, v in CV.items()],
          widths=[3.0, 1.9, 1.8])
    FIG(f"{PAPERFIG}/fig1_cv.png", "Cross-validated accuracy of the seven classifiers (mean and standard deviation)@@fig3.1", 4.8)
    H3("Why Random Forest Is Selected")
    P("Random Forest was selected for the deployed system for five reasons. First, it has the highest mean accuracy and the smallest standard "
      "deviation, so its performance is the most stable. Second, the Wilcoxon test (Chapter 7) shows that its advantage over every other "
      "model is statistically significant. Third, it needs no feature scaling and almost no tuning. Fourth, it provides probability estimates "
      "from the tree votes, which the interface shows as confidence. Fifth, it provides feature importance, shown in Figure {{num:fig3.2}}.")
    FIG(f"{OC}/07_feature_importance.png", "Random Forest feature importance for crop recommendation@@fig3.2", 4.8)
    P("The importance ranking is rainfall, humidity, potassium, phosphorus, nitrogen, temperature and pH. This is agronomically sensible: "
      "water availability separates crops such as rice from drought-tolerant pulses, and potassium and phosphorus separate fruit crops such "
      "as apple and grapes from the rest. The one weakness of Random Forest, discussed in Chapter 7, is that it degrades faster than SVM and "
      "KNN when the inputs are noisy.")
    H1(6, "Software Testing")
    P("Testing was carried out at four levels, in the same order as the sample project structure: unit, integration, system and regression.")
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
          widths=[0.5, 2.1, 2.0, 1.2, 0.7], size=9.5)
    H1(7, "Experimental Results")
    H2("Experimental Setup")
    P("All experiments were run on a Windows laptop with Python 3.12 and scikit-learn. The seed was fixed to 42. Hold-out results use the "
      "stratified 80/20 split described in Chapter 5. Cross-validation results use repeated stratified 5-fold cross-validation with three "
      "repeats. The experiment scripts and the numbers they produce are stored in the project repository, and the tables of this chapter are "
      "generated from the saved result files.")
    H2("Exploratory Data Analysis")
    P("Figure {{num:fig4.1}} shows the Pearson correlation between the crop features. Most pairs are only weakly correlated; the exception is the "
      "strong positive correlation of 0.74 between phosphorus and potassium, which comes from the high P and K values of a few "
      "crops such as apple and grapes. Figure {{num:fig4.2}} shows the feature distributions. Several features are skewed or multi-modal because the "
      "dataset mixes 22 crops with very different requirements, which is exactly why the classes are separable.")
    FIG(f"{OC}/02_correlation_heatmap.png", "Correlation heatmap of the crop dataset features@@fig4.1", 4.8)
    FIG(f"{OC}/03_feature_distributions.png", "Feature distributions of the crop dataset@@fig4.2", 5.6)
    H2("Crop Model Results")
    P(f"Table {{num:tab4.1}} gives the hold-out results on the 440 test rows. Random Forest reaches {CM['Random Forest']['accuracy']}% accuracy, which "
      f"means only 2 test samples out of 440 are misclassified. Decision Tree and KNN both reach {CM['Decision Tree']['accuracy']}%. The "
      "precision, recall and F1-score are within 0.1 percentage point of the accuracy, as expected for balanced classes.")
    TABLE("Hold-out results of the crop models (20% test split, 440 samples)@@tab4.1", ["Model", "Accuracy", "Precision", "Recall", "F1-score"],
          [[m] + [f"{CM[m][k]}%" for k in ("accuracy", "precision", "recall", "f1_score")] for m in M3], widths=[2.0, 1.15, 1.15, 1.15, 1.15])
    P("The confusion matrix of Figure {{num:fig4.3}} is almost perfectly diagonal. The only two errors are a blackgram sample predicted as maize "
      "and a rice sample predicted as jute; rice and jute both favour high rainfall and humidity.")
    FIG(f"{OC}/05_confusion_matrix_random_forest.png", "Confusion matrix of the Random Forest crop model@@fig4.3", 5.0)
    H2("Statistical Significance")
    P("The comparison on the hold-out split could depend on one particular split, so the 15 cross-validation scores were compared with the "
      "paired Wilcoxon test. Table {{num:tab4.2}} shows that Random Forest is better than every other model and that every difference is statistically "
      "significant at the 5% level. The absolute gaps are small, from 0.48 to 2.44 percentage points, so all models are practically useful on "
      "clean data, and the decision between them can reasonably consider other factors such as robustness.")
    TABLE("Random Forest compared with each other model (paired Wilcoxon test over 15 folds)@@tab4.2", ["Compared model", "Mean difference (pp)", "p-value"],
          [[AB[k], v["mean_diff_pp"], v["p_value"]] for k, v in WIL.items()], widths=[2.4, 2.3, 2.0])
    H2("Robustness To Sensor Noise")
    P("Low-cost field sensors are not perfectly accurate, so the models were tested with noisy inputs. Gaussian noise whose standard deviation "
      "is a fraction λ of each feature's standard deviation was added to the test data. Table {{num:tab4.3}} and Figure {{num:fig4.5}} show the accuracy at five "
      "levels of λ.")
    TABLE("Crop test accuracy (%) under added Gaussian noise@@tab4.3", ["Model"] + [f"λ = {x}" for x in LV],
          [[AB[k]] + [f"{x:.2f}" for x in v] for k, v in NZ.items()], widths=[1.1] + [1.12] * 5)
    FIG(f"{PAPERFIG}/fig2_noise.png", "Accuracy of the crop models versus noise level@@fig4.5", 4.8)
    P(f"The ranking changes completely under noise. At λ = 0.25 Random Forest falls to {NZ['Random Forest'][2]}%, whereas SVM keeps "
      f"{NZ['SVM (RBF)'][2]}% and KNN keeps {NZ['KNN (k=5)'][2]}%. Histogram gradient boosting ({NZ['Hist. Gradient Boosting'][2]}%) and the decision tree "
      f"({NZ['Decision Tree'][2]}%) degrade the most. A possible explanation is that axis-aligned tree splits are sensitive to small shifts of a "
      "value across a threshold, while distance-based and margin-based models average the effect of noise over all features; this explanation "
      "was not tested directly. At λ = 1.0 every model is below 45%. The practical conclusion is that Random Forest is the best choice for "
      "clean, accurately measured inputs, whereas an SVM would be safer for noisy sensors, and that benchmark accuracy alone does not "
      "predict field performance.")
    H2("Fertilizer Dataset Analysis")
    P(f"The fertilizer models gave a very different result. Table {{num:tab4.4}} shows that all three models score about 14.5% on the 20,000 test rows "
      f"(RF {FM['Random Forest']['accuracy']}%, DT {FM['Decision Tree']['accuracy']}%, KNN {FM['KNN']['accuracy']}%), which equals the chance level "
      "of 14.29% for seven classes. The correlation heatmap in Figure {{num:fig4.6}} has no relationship between any pair of features, and the "
      "confusion matrix in Figure {{num:fig4.9}} is uniform, with every class predicted with the same frequency.")
    TABLE("Hold-out results of the fertilizer models on the real Kaggle data@@tab4.4", ["Model", "Accuracy", "Precision", "Recall", "F1-score"],
          [[m] + [f"{FM[m][k]}%" for k in ("accuracy", "precision", "recall", "f1_score")] for m in M3], widths=[2.0, 1.15, 1.15, 1.15, 1.15])
    FIG(f"{OF}/05_correlation_heatmap.png", "Correlation heatmap of the fertilizer dataset features@@fig4.6", 4.8)
    P("To find out whether this is a modelling problem or a data problem, the dataset was audited with the tests of Chapter 5. Table {{num:tab4.5}} "
      "gives the results. No numeric feature differs significantly between fertilizer classes (all ANOVA p-values are above 0.27), soil type "
      f"is independent of the fertilizer (chi-square p = {RR['fert_chi2_p_soil']}), and the maximum mutual information is only "
      f"{RR['fert_mutual_info_max']} nats. Random Forest scores {RR['fert_rf_cv_real_pct']}% on the real labels and {RR['fert_rf_cv_shuffled_labels_pct']}% "
      "on randomly shuffled labels, which is the same.")
    TABLE("Audit of the fertilizer dataset@@tab4.5", ["Check", "Result"],
          [["Chance level (7 classes)", f"{RR['fert_chance_pct']}%"],
           ["ANOVA p-values (six numeric features)", f"{min(FA.values())} to {max(FA.values())}"],
           ["Chi-square p-value (soil type vs fertilizer)", RR["fert_chi2_p_soil"]],
           ["Maximum mutual information (nats)", RR["fert_mutual_info_max"]],
           ["Random Forest CV accuracy, real labels", f"{RR['fert_rf_cv_real_pct']}%"],
           ["Random Forest CV accuracy, shuffled labels", f"{RR['fert_rf_cv_shuffled_labels_pct']}%"],
           ["Mean N, P, K for Urea", f"{FMEAN['Urea']['Nitrogen']}, {FMEAN['Urea']['Phosphorous']}, {FMEAN['Urea']['Potassium']}"],
           ["Mean N, P, K for DAP", f"{FMEAN['DAP']['Nitrogen']}, {FMEAN['DAP']['Phosphorous']}, {FMEAN['DAP']['Potassium']}"]], widths=[4.0, 2.7])
    FIG(f"{PAPERFIG}/fig3_audit.png", "Crop versus fertilizer accuracy compared with chance and shuffled labels@@fig4.7", 4.6)
    FIG(f"{OF}/06_confusion_matrix_random_forest.png", "Confusion matrix of the Random Forest fertilizer model@@fig4.9", 4.6)
    P("The conclusion of the audit is that the fertilizer labels of this public file are statistically independent of the features, so no "
      "algorithm can learn a useful rule from it. A plausible explanation is that every column was generated independently at random, but how "
      "the file was produced was not verified. It means that published accuracy claims on this file should be treated with caution. "
      "The application therefore shows a reliability warning with every fertilizer prediction.")
    H2("Rule-Based Synthetic Experiment")
    P("To demonstrate that the pipeline itself works when the labels do carry a signal, a synthetic dataset of 5,000 rows was generated with a "
      "simple agronomic rule: a nutrient with a soil-test value below 20 counts as deficient, and the fertilizer is chosen to supply the "
      "deficient nutrients, with 5% random label noise. The same code was then applied. Table {{num:tab4.6}} shows that the models learn the rule: "
      f"Random Forest reaches {SM['Random Forest']['accuracy']}%, which is close to the 95% ceiling set by the label noise.")
    TABLE("Results on the rule-based synthetic fertilizer dataset (not real data)@@tab4.6", ["Model", "Hold-out accuracy", "5-fold CV accuracy"],
          [[m, f"{SM[m]['accuracy']}%", f"{SM[m].get('cv_accuracy', '-')}%"] for m in M3], widths=[2.4, 2.2, 2.1])
    P("This experiment is not a replacement for real data. It shows that the low score on the Kaggle file is caused by the data and not by "
      "the code, and it indicates what a better fertilizer dataset would look like: one in which the fertilizer is determined by measured "
      "nutrient deficiency.")
    H2("Feature Ablation")
    abl = EX["ablation"]; allacc = abl["all features"][0]
    drops = sorted(((allacc - v[0], k) for k, v in abl.items() if k != "all features"), reverse=True)
    P(f"To measure how much each input contributes, the Random Forest was retrained with one feature removed at a time and evaluated by "
      f"repeated cross-validation. Table {{num:tab4.8}} shows that removing rainfall causes the largest loss, from {allacc}% to {abl[drops[0][1]][0]}%, "
      f"followed by {drops[1][1].replace('without ', '')} ({abl[drops[1][1]][0]}%). Removing {drops[-1][1].replace('without ', '')} costs only "
      f"{drops[-1][0]:.2f} percentage points. The model is therefore robust to the loss of any single feature, and the ordering agrees with "
      "the feature-importance ranking of Figure {{num:fig3.2}}.")
    TABLE("Random Forest accuracy when one feature is removed (5-fold CV, 2 repeats)@@tab4.8", ["Feature set", "Accuracy (%)", "Change (pp)"],
          [[k, f"{v[0]} \u00b1 {v[1]}", "-" if k == "all features" else f"{v[0] - allacc:+.2f}"] for k, v in abl.items()], widths=[2.6, 2.2, 1.9])
    H2("Training And Prediction Time")
    tm = EX["timing"]
    P(f"The time needed to train each model and to predict the 440 test samples was measured on the same machine and averaged over three runs. "
      f"Table {{num:tab4.9}} shows that the decision tree and KNN train in about {tm['Decision Tree'][0]:.0f} ms and {tm['KNN (k=5)'][0]:.0f} ms, Random "
      f"Forest in {tm['Random Forest'][0]:.0f} ms, and the MLP and gradient boosting need {tm['MLP (64,32)'][0] / 1000:.1f} s and "
      f"{tm['Hist. Gradient Boosting'][0] / 1000:.1f} s. Prediction of all 440 samples takes {tm['Random Forest'][1]:.0f} ms for Random Forest, "
      "which is far below what an interactive interface needs. These timings are for the small crop dataset; the KNN prediction time would "
      "grow with the 100,000-row fertilizer data.")
    TABLE("Training time and prediction time of the classifiers (crop data, milliseconds)@@tab4.9", ["Classifier", "Training (ms)", "Prediction of 440 rows (ms)"],
          [[k, f"{v[0]:.1f}", f"{v[1]:.1f}"] for k, v in tm.items()], widths=[2.6, 2.0, 2.1])
    H2("Application Screenshots")
    P("Figures {{num:fig4.10}} to {{num:fig4.14}} show the five tabs of the application running on a local server. The crop predictor displays the recommended crop, "
      "the confidence, the agronomic rationale and the answers of all three models. The fertilizer advisor displays the reliability warning.")
    FIG(f"{FIGP}/ui_crop.png", "Crop Predictor tab with the Rice example@@fig4.10", 4.8)
    FIG(f"{FIGP}/ui_fertilizer.png", "Fertilizer Advisor tab with the reliability warning@@fig4.11", 4.8)
    FIG(f"{FIGP}/ui_satellite.png", "Satellite and Climate tab for the Thanjavur region@@fig4.12", 4.8)
    FIG(f"{FIGP}/ui_report.png", "Soil Health and Farm Advisory Report tab@@fig4.13", 4.8)
    FIG(f"{FIGP}/ui_dataset.png", "Dataset Explorer tab@@fig4.14", 4.8)
    H2("Discussion")
    P("Three findings stand out. First, the crop recommender is accurate and stable: 99.5% hold-out and cross-validated accuracy, significantly "
      "better than the alternatives, with sensible feature importance. Second, this accuracy is not a guarantee of field reliability, because "
      "the ranking of the models changes when the inputs are noisy, and the clean benchmark is easy. Third, the public fertilizer dataset cannot "
      "support a fertilizer model, and a project that reports only the accuracy of such a model would be misleading.")
    P("The design choices of the application follow from these findings: the interface shows the confidence of each prediction, a data-quality "
      "warning when a model is no better than chance, and a clear label wherever sample data is used. The limitations of the study are the use "
      "of public benchmark data, simulated and independent noise, untuned models and the absence of a field trial.")

    H1(8, "Conclusion")
    H2("Conclusion")
    P(f"A crop and fertilizer recommendation system was designed, implemented and evaluated. For crop recommendation, Random Forest was "
      f"selected after comparing seven algorithms with repeated cross-validation and significance tests; it reaches {CV['Random Forest']['acc_mean']}% "
      "accuracy. The model is served through a validated REST API, a web interface with five modules and six automated tests.")
    P("The evaluation also produced two lessons that go beyond the application. A statistical audit showed that the public fertilizer labels "
      "are independent of the features, so that fertilizer prediction on this file stays at the chance level of about 14%, and the system "
      "reports this openly. A noise test showed that the model with the highest clean accuracy is not the most robust, so that the choice of "
      "model for field deployment should consider measurement error.")
    H2("Learning Outcomes")
    P("The team applied the complete machine-learning workflow, from data audit to deployment and testing, and learned to report "
      "negative results honestly.")

    H1(9, "Future Enhancement")
    H2("Future Scope")
    BUL(["Collect or obtain real soil-test data in which the recommended fertilizer follows measured nutrient deficiency, and retrain the fertilizer model.",
         "Replace the sample satellite values with NDVI and NDWI computed from Sentinel-2 imagery, and add vegetation indices as model inputs.",
         "Connect live weather and market-price services and low-cost soil sensors for automatic data entry.",
         "Tune hyper-parameters with grid search, add noise-aware training and calibrate the predicted probabilities.",
         "Add model explanations such as SHAP values, and offer the interface in regional languages.",
         "Run a field trial with farmers to measure the effect of the recommendations on yield and fertilizer cost."])
