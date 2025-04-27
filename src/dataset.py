import streamlit as st
from libs.dataset import DatasetStorage

DATASET_STORAGE = DatasetStorage()


def init():
    if "datasets" not in st.session_state:
        st.session_state.datasets = DATASET_STORAGE.list_datasets()


def manage_datasets():
    init()

    st.title("Dataset Management")

    action = st.radio("작업 선택", ("데이터셋 선택", "새 데이터셋 생성"))

    if action == "데이터셋 선택":
        st.selectbox("데이터셋 선택", st.session_state.datasets, key="selected_dataset")

        if st.session_state.selected_dataset:
            dataset = DATASET_STORAGE.get_dataset(st.session_state.selected_dataset)
            entries = dataset.get_entries()
            st.dataframe(entries, use_container_width=True)

            with st.expander("Add Entry Form"):
                with st.container():
                    st.caption("input_variables")
                    st.number_input("number of keys", value=1, key="input_variables_number")
                    for n in range(0, st.session_state.input_variables_number):
                        key, value = st.columns(2)
                        key.text_input(label="key", key=f"input_variables_key_{n}")
                        value.text_input(label="value", key=f"input_variables_value_{n}")
                st.text_input(label="reference_output", key="reference_output")
                with st.container():
                    st.caption("metadata")
                    st.number_input("number of keys", value=0, key="metadata_number")
                    for n in range(0, st.session_state.metadata_number):
                        key, value = st.columns(2)
                        key.text_input(label="key", key=f"metadata_key_{n}")
                        value.text_input(label="value", key=f"metadata_value_{n}")

            if st.button("Add Entry"):
                input_variables = {}
                for n in range(0, st.session_state.input_variables_number):
                    key = st.session_state[f"input_variables_key_{n}"]
                    value = st.session_state[f"input_variables_value_{n}"]
                    input_variables[key] = value
                reference_output = st.session_state.reference_output
                metadata = {}
                for n in range(0, st.session_state.metadata_number):
                    key = st.session_state[f"metadata_key_{n}"]
                    value = st.session_state[f"metadata_value_{n}"]
                    metadata[key] = value
                dataset.add_entry(input_variables, reference_output, metadata)
                st.toast('성공적으로 데이터가 추가되었습니다!', icon='🎉')

            if st.button("Delete Dataset"):
                DATASET_STORAGE.delete_dataset(st.session_state.selected_dataset)
                st.session_state.datasets = DATASET_STORAGE.list_datasets()
                st.toast('데이터셋이 삭제되었습니다')

    elif action == "새 데이터셋 생성":
        new_dataset_name = st.text_input("새 데이터셋 이름")
        if st.button("Create Dataset"):
            DATASET_STORAGE.create_dataset(new_dataset_name)
            st.session_state.datasets = DATASET_STORAGE.list_datasets()
            st.toast('성공적으로 데이터셋이 생성되었습니다!', icon='🎉')


manage_datasets()
