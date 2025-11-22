import streamlit as st

def main():
    st.set_page_config(page_title="Super App", page_icon=":rocket:")

    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio("Go to", ["Home", "Mini App 1", "Mini App 2", "Mini App 3"])

    if app_choice == "Home":
        show_home_page()
    elif app_choice == "Mini App 1":
        show_mini_app_1()
    elif app_choice == "Mini App 2":
        show_mini_app_2()
    elif app_choice == "Mini App 3":
        show_mini_app_3()

def show_home_page():
    st.title("Welcome to the Super App!")
    st.write("This is the central hub for all our amazing mini-applications.")
    st.write("Please select a mini-app from the navigation sidebar to get started.")

def show_mini_app_1():
    st.header("Mini App 1")
    st.write("This is the first mini-application.")
    # Add your Mini App 1 code here

def show_mini_app_2():
    st.header("Mini App 2")
    st.write("This is the second mini-application.")
    # Add your Mini App 2 code here

def show_mini_app_3():
    st.header("Mini App 3")
    st.write("This is the third mini-application.")
    # Add your Mini App 3 code here

if __name__ == "__main__":
    main()
