import streamlit as st
import pandas as pd
st.set_page_config(page_title="mdm")

file = st.file_uploader("upload file" ,type=["csv"])
seats = st.number_input("seat limit",value=10)
button = st.button("Upload")

major = ["aids" , "cs" , "civil" , "mech" ]
minor = {
    "aids" : ["cs" , "civil" , "mech" ],
    "cs" : ["civil" , "mech" ],
    "civil" : ["mech"],
    "mech" : ["civil"]
}

if file and button:
    data = pd.read_csv(file)
    st.write("Uploaded Data")
    st.dataframe(data)
    sorted_data = data.sort_values(by = ["Backlog" , "Percentage"] , ascending = [True,False])
    grouped_data = sorted_data.groupby("Branch", sort=False)
    grouped_data = {branch: group.copy() for branch, group in sorted_data.groupby("Branch", sort=False)}
    for branch, df in grouped_data.items():
        allowed_minors = minor[branch]
        df["Minor"] = None 
        for i in range(len(df)):
            minor_idx = i // seats
            if minor_idx < len(allowed_minors):
                df.iloc[i, df.columns.get_loc("Minor")] = allowed_minors[minor_idx]
            else:
                df.iloc[i, df.columns.get_loc("Minor")] = None
    final_data = (pd.concat(grouped_data.values(), ignore_index=True).sort_index())
    st.write("Assigned minor")
    st.dataframe(final_data)