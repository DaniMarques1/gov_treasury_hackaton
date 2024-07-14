import streamlit as st
import os

st.set_page_config(
    page_title="Axie Infinity Treasury Hackathon!"
)

st.sidebar.success("Select the page above.")
st.markdown(f"<h1>The Axie Infinity Treasury</h1>", unsafe_allow_html=True)

image_path = os.path.join(os.path.dirname(__file__), 'img', 'gov.png')
st.image(image_path, width=300)  # Adjust the width as needed

st.markdown("""
The Axie Infinity Treasury is a key component of the Axie Infinity ecosystem, serving as a repository for the game's financial transactions. The treasury collects funds from various sources, including:

1. **Marketplace Fees**: A portion of the fees generated from transactions in the Axie Infinity marketplace, where players buy and sell Axies, land, and other assets.
2. **Breeding Fees**: Fees collected when players breed Axies to create new ones.
3. **Ascending Axies and Parts Evolution**: Fees collected when players ascend and evolve their Axies.
4. **R&C Mint**: Origins Runes and Charms minting fees.

The funds accumulated in the treasury are distributed for various ecosystem purposes, including:

- **Governance**: Allowing AXS token holders to vote on important decisions regarding the game's future, including the use of treasury funds.
- **Ecosystem Growth**: Investing in initiatives that promote the growth and expansion of the Axie Infinity ecosystem.

Overall, the Axie Infinity Treasury plays a crucial role in the sustainable growth and development of the Axie Infinity game and its community by ensuring that there are sufficient resources to support various initiatives and maintain the game's operations.

**This charts reveals how many tokens are being sent to the Community Treasury, and its main goal is to help with distribution decision-making.**
""")
