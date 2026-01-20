import streamlit as st
import pandas as pd
st.set_page_config(page_title="mdm")

file = st.file_uploader("upload file" ,type=["csv"])
seats = st.number_input("seat limit",value=10)
button = st.button("Upload")

major = ["aids" , "cs" , "civil" , "mech" ,"e&tc"]
minor = {
    "aids" : ["e&tc" , "civil" , "mech" ],
    "cs" : ["e&tc","civil" , "mech" ],
    "civil" : ["aids","cs","e&tc","mech"],
    "mech" : ["aids","cs","e&tc","civil"]
}

if file and button:
    data = pd.read_csv(file)
    st.write("Uploaded data")
    st.dataframe(data)
    data = data.sort_values(by=["Backlog", "Percentage"],ascending=[True, False])
    data["Minor"] = None
    minor_seats = { branch: {m: seats for m in minors} for branch, minors in minor.items()}
    
    for branch in data["Branch"].unique():
        branch_students = data[data["Branch"] == branch]
        
        for idx, row in branch_students.iterrows():
            assigned = False

            for choice_col in ["Choice1", "Choice2", "Choice3"]:
                choice = row.get(choice_col).lower()
                if ( choice in minor_seats[branch] and minor_seats[branch][choice] > 0):
                    data.at[idx, "Minor"] = choice
                    minor_seats[branch][choice] -= 1
                    assigned = True
                    break

            if not assigned:
                for m, count in minor_seats[branch].items():
                    if count > 0:
                        data.at[idx, "Minor"] = m
                        minor_seats[branch][m] -= 1
                        assigned = True
                        break

    final_data = data.sort_values(by=["Branch", "Backlog", "Percentage"],ascending=[True, True, False]).reset_index(drop=True)

    st.write("Assigned minor")
    st.dataframe(final_data)
