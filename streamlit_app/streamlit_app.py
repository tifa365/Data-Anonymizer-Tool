import pathlib
import pandas as pd
import streamlit as st
import tempfile


from DataSynthesizer.DataDescriber import DataDescriber
from DataSynthesizer.datatypes.utils.DataType import DataType
from DataSynthesizer.datatypes.StringAttribute import StringAttribute
from DataSynthesizer.DataGenerator import DataGenerator
from DataSynthesizer.lib.utils import (
    read_json_file,
    pairwise_attributes_mutual_information,
)

import sklearn.linear_model as sklmodel
import plotly.subplots as sp
import plotly.graph_objs as go
import numpy as np

from typing import Tuple
from express_model_inspector import ExpressModelInspector

TITLE = "Data Anonymization Tool"

folder = pathlib.Path(__file__).parent

github_svg = """
<svg fill="white" height="24" aria-hidden="true" viewBox="0 0 16 16" version="1.1" width="32" data-view-component="true">
    <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
</svg>
"""

nextbrain_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="24" viewBox="0 0 32 24" fill="white">
    <path fill-rule="evenodd" clip-rule="evenodd" d="M31.9758 13.9946L29.3906 4.6293C29.0847 3.51942 27.8983 2.85459 26.7544 3.15129C26.5165 3.21448 26.2985 3.31338 26.1031 3.43975C25.3669 3.92601 24.9874 4.82985 25.231 5.70896L27.9889 15.6924C28.088 16.055 27.8643 16.4314 27.4906 16.5303C27.1168 16.6264 26.7289 16.4094 26.6269 16.0468L22.7788 2.11834C22.5353 1.23922 21.7425 0.640328 20.8533 0.577142C20.6211 0.560658 20.3805 0.579889 20.1426 0.643075C19.9048 0.706261 19.6867 0.805161 19.4913 0.931534C18.7551 1.41779 18.3757 2.32163 18.6192 3.20074L23.5801 21.1648C23.6793 21.5275 23.4556 21.9039 23.0818 22.0028C22.708 22.0989 22.3201 21.8819 22.2182 21.5192L16.9288 2.36284C16.6852 1.48373 15.8924 0.884831 15.0033 0.821645C14.7711 0.805161 14.5304 0.824392 14.2926 0.887578C14.0547 0.950764 13.8367 1.04966 13.6413 1.17604C12.9079 1.65955 12.5285 2.55789 12.7663 3.43426V3.44525L16.4672 16.838C16.5635 17.2006 16.3398 17.5715 15.966 17.6676C15.5923 17.7638 15.2043 17.5468 15.1024 17.1841L11.4666 4.00293C11.2231 3.12382 10.4303 2.52492 9.54116 2.46174C9.30897 2.44525 9.06828 2.46449 8.83043 2.52767C8.59258 2.59086 8.37455 2.68976 8.17917 2.81613C7.44579 3.29964 7.06635 4.19798 7.30421 5.07435V5.08534L10.2915 15.8847C10.3878 16.2446 10.1641 16.6182 9.79034 16.7143C9.41657 16.8105 9.02864 16.5935 8.92671 16.2308L6.39244 7.05785C6.14892 6.17873 5.35608 5.57984 4.46696 5.51665C4.23477 5.50017 3.99409 5.5194 3.75623 5.58259C3.51838 5.64577 3.30035 5.74467 3.10497 5.87105C2.37159 6.35456 1.99216 7.2529 2.23001 8.12926L3.9771 14.4589V14.4644C4.07337 14.827 3.84967 15.1979 3.47874 15.294C3.10497 15.3902 2.71704 15.1732 2.6151 14.8105L1.42301 10.4946C1.32107 10.121 0.921818 9.89848 0.536722 9.99738C0.151627 10.0963 -0.0777312 10.4836 0.0242058 10.8573L1.2163 15.1732C1.52211 16.283 2.70855 16.9479 3.85251 16.6512C4.09036 16.588 4.30839 16.4891 4.50377 16.3627C5.23998 15.8764 5.61942 14.9726 5.3759 14.0935L3.63164 7.77487C3.53254 7.41224 3.75623 7.03587 4.13 6.93697C4.50094 6.84082 4.88887 7.0551 4.9908 7.41499V7.42048L7.52507 16.5935C7.52507 16.5935 7.52507 16.6017 7.5279 16.6045C7.77425 17.4753 8.56426 18.0715 9.45055 18.1347C9.68274 18.1511 9.92342 18.1319 10.1613 18.0687C10.3991 18.0055 10.6172 17.9066 10.8125 17.7803C11.5488 17.294 11.9282 16.3902 11.6847 15.5111L8.70584 4.7227C8.60674 4.36007 8.83043 3.9837 9.2042 3.8848C9.57514 3.78865 9.96307 4.00293 10.065 4.36282V4.36831L13.7036 17.5468C13.7036 17.5468 13.7036 17.555 13.7064 17.5577C13.9528 18.4286 14.7428 19.0248 15.6291 19.0879C15.8613 19.1044 16.1019 19.0852 16.3398 19.022C16.5776 18.9588 16.7957 18.8599 16.9911 18.7336C17.7273 18.2473 18.1067 17.3435 17.8632 16.4643L14.168 3.07986C14.0689 2.71723 14.2926 2.34086 14.6663 2.24196C15.0373 2.14581 15.4252 2.36009 15.5271 2.71998V2.72547L20.8165 21.8819C20.8165 21.8819 20.8165 21.8901 20.8194 21.8929C21.0657 22.7637 21.8557 23.3599 22.742 23.4231C22.9742 23.4396 23.2149 23.4203 23.4527 23.3571C23.6906 23.2939 23.9086 23.195 24.104 23.0687C24.8402 22.5824 25.2196 21.6786 24.9761 20.7995L20.018 2.83811C19.9189 2.47547 20.1426 2.0991 20.5164 2.0002C20.8901 1.90405 21.2781 2.12108 21.38 2.48372L25.2281 16.4121C25.4716 17.2913 26.2645 17.8902 27.1536 17.9533C27.3858 17.9698 27.6265 17.9506 27.8643 17.8874C28.1022 17.8242 28.3202 17.7253 28.5156 17.599C29.2518 17.1127 29.6312 16.2089 29.3877 15.3297L26.6298 5.34632C26.5307 4.98369 26.7544 4.60732 27.1281 4.50842C27.5019 4.41227 27.8898 4.6293 27.9918 4.99193L30.577 14.3572C30.6789 14.7308 31.0782 14.9534 31.4633 14.8545C31.8484 14.7556 32.0777 14.3682 31.9758 13.9946Z" fill="white"/>
<script xmlns=""/></svg>
"""

windows_svg = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:v="https://vecta.io/nano" height="24" width="24" viewBox="0 0 88 88">
    <path d="M0 12.402l35.687-4.86.016 34.423-35.67.203zm35.67 33.529l.028 34.453L.028 75.48.026 45.7zm4.326-39.025L87.314 0v41.527l-47.318.376zm47.329 39.349l-.011 41.34-47.318-6.678-.066-34.739z" fill="#00adef"/><script xmlns=""/>
</svg>
"""

linux_svg = """
<svg fill="white" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
    <path d="M20.581 19.049c-.55-.446-.336-1.431-.907-1.917.553-3.365-.997-6.331-2.845-8.232-1.551-1.595-1.051-3.147-1.051-4.49 0-2.146-.881-4.41-3.55-4.41-2.853 0-3.635 2.38-3.663 3.738-.068 3.262.659 4.11-1.25 6.484-2.246 2.793-2.577 5.579-2.07 7.057-.237.276-.557.582-1.155.835-1.652.72-.441 1.925-.898 2.78-.13.243-.192.497-.192.74 0 .75.596 1.399 1.679 1.302 1.461-.13 2.809.905 3.681.905.77 0 1.402-.438 1.696-1.041 1.377-.339 3.077-.296 4.453.059.247.691.917 1.141 1.662 1.141 1.631 0 1.945-1.849 3.816-2.475.674-.225 1.013-.879 1.013-1.488 0-.39-.139-.761-.419-.988zm-9.147-10.465c-.319 0-.583-.258-1-.568-.528-.392-1.065-.618-1.059-1.03 0-.283.379-.37.869-.681.526-.333.731-.671 1.249-.671.53 0 .69.268 1.41.579.708.307 1.201.427 1.201.773 0 .355-.741.609-1.158.868-.613.378-.928.73-1.512.73zm1.665-5.215c.882.141.981 1.691.559 2.454l-.355-.145c.184-.543.181-1.437-.435-1.494-.391-.036-.643.48-.697.922-.153-.064-.32-.11-.523-.127.062-.923.658-1.737 1.451-1.61zm-3.403.331c.676-.168 1.075.618 1.078 1.435l-.31.19c-.042-.343-.195-.897-.579-.779-.411.128-.344 1.083-.115 1.279l-.306.17c-.42-.707-.419-2.133.232-2.295zm-2.115 19.243c-1.963-.893-2.63-.69-3.005-.69-.777 0-1.031-.579-.739-1.127.248-.465.171-.952.11-1.343-.094-.599-.111-.794.478-1.052.815-.346 1.177-.791 1.447-1.124.758-.937 1.523.537 2.15 1.85.407.851 1.208 1.282 1.455 2.225.227.871-.71 1.801-1.896 1.261zm6.987-1.874c-1.384.673-3.147.982-4.466.299-.195-.563-.507-.927-.843-1.293.539-.142.939-.814.46-1.489-.511-.721-1.555-1.224-2.61-2.04-.987-.763-1.299-2.644.045-4.746-.655 1.862-.272 3.578.057 4.069.068-.988.146-2.638 1.496-4.615.681-.998.691-2.316.706-3.14l.62.424c.456.337.838.708 1.386.708.81 0 1.258-.466 1.882-.853.244-.15.613-.302.923-.513.52 2.476 2.674 5.454 2.795 7.15.501-1.032-.142-3.514-.142-3.514.842 1.285.909 2.356.946 3.67.589.241 1.221.869 1.279 1.696l-.245-.028c-.126-.919-2.607-2.269-2.83-.539-1.19.181-.757 2.066-.997 3.288-.11.559-.314 1.001-.462 1.466zm4.846-.041c-.985.38-1.65 1.187-2.107 1.688-.88.966-2.044.503-2.168-.401-.131-.966.36-1.493.572-2.574.193-.987-.023-2.506.431-2.668.295 1.753 2.066 1.016 2.47.538.657 0 .712.222.859.837.092.385.219.709.578 1.09.418.447.29 1.133-.635 1.49zm-8-13.006c-.651 0-1.138-.433-1.534-.769-.203-.171.05-.487.253-.315.387.328.777.675 1.281.675.607 0 1.142-.519 1.867-.805.247-.097.388.285.143.382-.704.277-1.269.832-2.01.832z"/>
</svg>
"""

apple_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 842.32007 1000.0001">
  <path fill="#b3b3b3" d="M824.66636 779.30363c-15.12299 34.93724-33.02368 67.09674-53.7638 96.66374-28.27076 40.3074-51.4182 68.2078-69.25717 83.7012-27.65347 25.4313-57.2822 38.4556-89.00964 39.1963-22.77708 0-50.24539-6.4813-82.21973-19.629-32.07926-13.0861-61.55985-19.5673-88.51583-19.5673-28.27075 0-58.59083 6.4812-91.02193 19.5673-32.48053 13.1477-58.64639 19.9994-78.65196 20.6784-30.42501 1.29623-60.75123-12.0985-91.02193-40.2457-19.32039-16.8514-43.48632-45.7394-72.43607-86.6641-31.060778-43.7024-56.597041-94.37983-76.602609-152.15586C10.740416 658.44309 0 598.01283 0 539.50845c0-67.01648 14.481044-124.8172 43.486336-173.25401C66.28194 327.34823 96.60818 296.6578 134.5638 274.1276c37.95566-22.53016 78.96676-34.01129 123.1321-34.74585 24.16591 0 55.85633 7.47508 95.23784 22.166 39.27042 14.74029 64.48571 22.21538 75.54091 22.21538 8.26518 0 36.27668-8.7405 83.7629-26.16587 44.90607-16.16001 82.80614-22.85118 113.85458-20.21546 84.13326 6.78992 147.34122 39.95559 189.37699 99.70686-75.24463 45.59122-112.46573 109.4473-111.72502 191.36456.67899 63.8067 23.82643 116.90384 69.31888 159.06309 20.61664 19.56727 43.64066 34.69027 69.2571 45.4307-5.55531 16.11062-11.41933 31.54225-17.65372 46.35662zM631.70926 20.0057c0 50.01141-18.27108 96.70693-54.6897 139.92782-43.94932 51.38118-97.10817 81.07162-154.75459 76.38659-.73454-5.99983-1.16045-12.31444-1.16045-18.95003 0-48.01091 20.9006-99.39207 58.01678-141.40314 18.53027-21.27094 42.09746-38.95744 70.67685-53.0663C578.3158 9.00229 605.2903 1.31621 630.65988 0c.74076 6.68575 1.04938 13.37191 1.04938 20.00505z"/>
<script xmlns=""/></svg>
"""

st.set_page_config(
    page_title=TITLE,
    page_icon=nextbrain_svg,
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def calc_accuracy(df: pd.DataFrame, synthetic_df: pd.DataFrame) -> float:
    df = df.copy()
    new_df = synthetic_df.copy()
    df["Synthetic"] = 0
    new_df["Synthetic"] = 1
    data = pd.concat([df, new_df.sample(len(df))]).dropna()
    numerical_columns = data.select_dtypes(include=["number"])
    data = data[numerical_columns.columns]
    X = data.drop(columns=["Synthetic"])
    y = data["Synthetic"]
    if y.unique()[0] <= 1:
        return 0
    clf = sklmodel.LogisticRegression(random_state=0).fit(X, y)
    pMSE = np.sum(np.square(clf.predict_proba(X)[0:, 0] - 0.5)) / len(data)
    return 100 * (1 - pMSE)


@st.cache_data
def anonymize(
    uploaded_file, num_rows: int = 100, algorithm_level: int = 1
) -> Tuple[pd.DataFrame, dict]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)
        csv_file = temp_dir / "data.csv"
        description_file = temp_dir / "describe.json"
        synthetic_data_file = temp_dir / "synthetic.csv"

        # Save the uploaded file content
        csv_file.write_bytes(uploaded_file.getvalue())

        # Try to read the CSV file
        try:
            df = pd.read_csv(csv_file, dtype=str)
            if df.empty:
                raise ValueError("The uploaded file is empty.")
        except pd.errors.EmptyDataError:
            raise ValueError("The uploaded file is empty or has no columns.")
        except Exception as e:
            raise ValueError(f"Error reading the uploaded file: {str(e)}")

        # Print information about the DataFrame
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"First few rows of the DataFrame:\n{df.head()}")

        describer = DataDescriber(category_threshold=20)
        describer.df_input = df
        describer.attr_to_column = {}

        # Force all columns to be treated as categorical strings
        describer.attr_to_datatype = {col: DataType.STRING for col in df.columns}
        describer.attr_to_is_categorical = {col: True for col in df.columns}

        # Override the represent_input_dataset_by_columns method
        def custom_represent(self):
            for attr in self.df_input:
                is_candidate_key = self.attr_to_is_candidate_key.get(attr, False)
                is_categorical = self.attr_to_is_categorical.get(attr, True)
                self.attr_to_column[attr] = StringAttribute(
                    attr,
                    is_candidate_key,
                    is_categorical,
                    self.histogram_bins,
                    self.df_input[attr],
                )

        # Apply the custom method
        describer.represent_input_dataset_by_columns = custom_represent.__get__(
            describer
        )

        level_to_describer_algorithm = {
            0: describer.describe_dataset_in_random_mode,
            1: describer.describe_dataset_in_independent_attribute_mode,
            2: describer.describe_dataset_in_correlated_attribute_mode,
        }

        # Generate description
        level_to_describer_algorithm[algorithm_level](csv_file)

        # Save description
        describer.save_dataset_description_to_file(description_file)

        generator = DataGenerator()
        level_to_generator_algorithm = {
            0: generator.generate_dataset_in_random_mode,
            1: generator.generate_dataset_in_independent_mode,
            2: generator.generate_dataset_in_correlated_attribute_mode,
        }

        # Generate synthetic data
        level_to_generator_algorithm[algorithm_level](
            num_rows, description_file=description_file
        )

        # Save synthetic data
        generator.save_synthetic_data(synthetic_data_file)

        return pd.read_csv(synthetic_data_file), read_json_file(description_file)


@st.cache_data
def convert_df(df: pd.DataFrame) -> str:
    return df.to_csv(index=False).encode("utf-8")


def calculate_heatmaps(df: pd.DataFrame, synthetic_df: pd.DataFrame):
    df_mi = pairwise_attributes_mutual_information(df)
    synthetic_mi = pairwise_attributes_mutual_information(synthetic_df)
    fig = sp.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "Private data correlation",
            "Synthetic data correlation",
            "Difference",
        ],
    )
    heatmap1 = go.Heatmap(z=df_mi.values, x=df_mi.columns, y=df_mi.index)
    fig.add_trace(heatmap1, row=1, col=1)
    heatmap2 = go.Heatmap(
        z=synthetic_mi.values, x=synthetic_mi.columns, y=synthetic_mi.index
    )
    fig.add_trace(heatmap2, row=1, col=2)
    fig.update_layout(height=800, showlegend=False)
    heatmap3 = go.Heatmap(
        z=(df_mi - synthetic_mi).values, x=synthetic_mi.columns, y=synthetic_mi.index
    )
    fig.add_trace(heatmap3, row=2, col=1)
    fig.update_layout(height=1400, showlegend=False)
    return fig


custom_styles = """
    <style>
    .main .block-container {
        display:flex;
        min-height:calc(100vh - 1rem);
        padding-bottom: 0;
        padding-top: 2rem;
    }
    .main  > *:nth-child(n+2){
        display:none
    }
    .main .block-container > div > div > div:nth-last-child(2)  > div {
        justify-content:flex-end;
    }
    .footer {
        align-self:end;
        width: 100%;
        text-align: center;
        display: flex;
        flex-wrap: wrap;
        padding-bottom: 30px;
        background-color: #011222;
    }
    .footer > div {
        flex: 1;
        text-align: center;
        flex-basis: 33.3%;
    }

    .footer > div:nth-child(1) {
        flex-basis: 90%;
        text-align: center;
    }

    .footer > div:nth-child(2) {
        text-align: right;
    }

    .footer > div:nth-child(3) {
        color: rgba(173, 186, 199, 0.6);
        font-size: 14px;
    }

    .img-container {
        display: flex;
    }

    .img-container svg, .img-container a {
        margin-right: 10px;
    }
    #data-anonymization-tool{
        padding-top: 0;
    }
    .highlight {
        color:white;
        font-weight:bold;
        text-decoration:underline;
    }
    .result-description{
        display: inline-block;
        font-size: 1.2rem;
        padding: 15px;
        border: 1px solid #192b3c;
        border-radius:8px;
        margin-bottom: 3.5rem;
    }
    .split-cols{
        display:flex;
        justify-content:space-between;
        margin-bottom:5px;
        flex-direction: row;
    }
    .split-cols > *:first-child{
        margin-right:50px;
    }
    </style>
"""

result_description = """
<div class="result-description">
    <div class="split-cols">
       <span>Rows in the original dataset</span> <span class="highlight">{0}</span>
    </div>
    <div class="split-cols">
       <span>Rows in the new dataset</span> <span class="highlight">{1}</span>
    </div>
    <div class="split-cols">
      <span>Columns</span> <span class="highlight">{2}</span>
    </div>
    <div class="split-cols">
      <span>Accuracy</span> <span class="highlight">{3}</span>
    </div>
</div>
"""

footer_html = f"""
<div class="footer">
    <div>
        <hr style="margin-top: 0px;" />
    </div>
    <div class="img-container" style="justify-content: end">
        {nextbrain_svg}<br/>
        <a href="https://nextbrain.ai" target="_blank">NextBrain</a>
    </div>
    <div>
        {windows_svg}{apple_svg}{linux_svg}<br/>
        Windows, Mac and Linux version coming soon
    </div>
    <div class="img-container">
        {github_svg}<br/>
        <a href="https://github.com/NextBrain-ai/Data-Anonymizer-Tool" target="_blank">GitHub Project</a>
    </div>
</div>
"""

st.markdown(custom_styles, unsafe_allow_html=True)

try:
    st.image(nextbrain_svg, width=50)
except Exception:
    st.write(" ")

st.title(TITLE)

description_placeholder = st.empty()
description_placeholder.write(
    "Data Anonymizer tool ensures top-tier privacy by irreversibly "
    "obscuring personal identifiers without storing any data. Ideal for businesses "
    "prioritizing data security and compliance, it offers a reliable solution for "
    "safeguarding sensitive information.\n\n"
    "See how to use it in your own servers or local pc: [Instructions](https://github.com/NextBrain-ai/Data-Anonymizer-Tool/blob/main/README.md)"
)

upload_placeholder = st.empty()
csv_file = upload_placeholder.file_uploader(
    "Select file",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
)

if csv_file is not None:
    description_placeholder.empty()
    upload_placeholder.empty()

    try:

        def load_and_preprocess_data(uploaded_file):
            # Read the CSV file
            df = pd.read_csv(uploaded_file, dtype=str)

            # Save the DataFrame as a CSV file
            df.to_csv(csv_file, index=False)

            print("Data loaded successfully:" + type(df).__name__)

            return df

        # In the anonymize function, replace the data loading part with:
        df = load_and_preprocess_data(csv_file)
        df.to_csv(csv_file, index=False)

        csv_placeholder = st.empty()
        csv_placeholder.write(df)
        options = [
            "Random mode (fast speed)",
            "Independent attribute mode (medium speed)",
            "Correlated attribute mode (low speed)",
        ]
        option_placeholder = st.empty()
        option = option_placeholder.selectbox(
            "Select your Anonymization algorithm (Optional)",
            options,
            index=1,
        )

        button_generate_synthetic_placeholder = st.empty()
        if button_generate_synthetic_placeholder.button("Anonymize"):
            button_generate_synthetic_placeholder.empty()
            csv_placeholder.empty()
            csv_placeholder.empty()
            option_placeholder.empty()

            algorithm_level = options.index(option)
            synthetic_df, description = anonymize(
                csv_file, num_rows=len(df), algorithm_level=algorithm_level
            )

            try:
                acc = round(calc_accuracy(df, synthetic_df), 2)
            except Exception:
                acc = 0

            st.markdown(
                result_description.format(
                    len(df),
                    len(synthetic_df),
                    len(synthetic_df.columns),
                    f"{acc}%" if acc is not None else "N/A",
                ),
                unsafe_allow_html=True,
            )
            st.write("Anonymized data:")
            st.write(synthetic_df)
            st.download_button(
                "Press to Download",
                convert_df(synthetic_df),
                "file.csv",
                "text/csv",
                key="download-csv",
                type="primary",
            )

            with st.expander("Statistics", expanded=False):
                tab1, tab2 = st.tabs(["Histograms", "Heatmaps"])

                with tab1:
                    inspector = ExpressModelInspector(
                        df, synthetic_df, description["attribute_description"]
                    )
                    for attribute in synthetic_df.columns:
                        try:
                            fig = inspector.compare_histograms(attribute)
                            if fig is None:
                                continue
                            st.plotly_chart(fig)
                        except Exception:
                            pass

                with tab2:
                    heatmaps = calculate_heatmaps(df, synthetic_df)
                    st.plotly_chart(heatmaps, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)

footer = st.empty()
with footer.container():
    st.markdown(footer_html, unsafe_allow_html=True)
