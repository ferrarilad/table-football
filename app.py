import streamlit as st

from utils import page_init

page_init("Work Hard, have fun, make history...⚽")

st.subheader("!!! This is not a classic tournament !!!")
st.write(
    """
The competition we are currently proposing is based on [ELO](https://en.wikipedia.org/wiki/Elo_rating_system) that is a method for calculating the relative skill levels of players.  
Each time you play a match your score increases by an amount that depends on your team average ELO and the opposing team average ELO.  

Maybe in September we will host a real tournament (who knows!) in the meantime lets make this RTO epic and get to know each other!  
"""
)
st.markdown("""---""")
st.write(
    """
  __TLDR:__  
If you win against a strong team you will gain a lot of points (maximum 40) if you lose against a strong team you will lose few points.
The higher you are in the ranking the strongest you are. 
"""
)
st.markdown("""---""")
st.subheader("Instructions")
st.write(
    """
To participate to the competition: 
1. Only the first time: select \"Player Registration\" and add your identifier\n

2. Play a match\n
3. Register the game in the \"Register match\" section\n
4. See your ranking in  \"Player Ranking\"

See you on slack: ```#lin11-table-football```.
"""
)


def main():
    # st.header("Work Hard, have fun, make history...⚽")

    st.sidebar.subheader("Instructions")
    st.sidebar.write(
        """
    To participate to the competition: 
    1. Only the first time: select \"Player Registration\" and add your identifier\n
    2. Play a match\n
    3. Register the game in the \"Register match\" section\n
    4. See your ranking in  \"Player Ranking\"
    """
    )


if __name__ == "__main__":
    main()
