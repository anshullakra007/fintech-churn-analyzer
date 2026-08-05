import streamlit as st
import streamlit.components.v1 as components

def render():
    st.markdown("<br>", unsafe_allow_html=True)
    # --- Tableau Embed Example ---
    tableau_html = """
    <div class='tableauPlaceholder' id='viz1' style='position: relative; width: 100%; height: 800px;'>
        <noscript><a href='#'><img alt='Dashboard' src='' style='border: none' /></a></noscript>
        <object class='tableauViz'  style='display:none;'>
            <param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> 
            <param name='embed_code_version' value='3' /> 
            <param name='site_root' value='' />
            <param name='name' value='FinTechChurnAnalysis/Sheet1' />
            <param name='tabs' value='yes' />
            <param name='toolbar' value='yes' />
            <param name='animate_transition' value='yes' />
            <param name='display_static_image' value='yes' />
            <param name='display_spinner' value='yes' />
            <param name='display_overlay' value='yes' />
            <param name='display_count' value='yes' />
            <param name='language' value='en-US' />
        </object>
    </div>
    <script type='text/javascript'>
        var divElement = document.getElementById('viz1');
        var vizElement = divElement.getElementsByTagName('object')[0];
        vizElement.style.width='100%';vizElement.style.height='800px';
        var scriptElement = document.createElement('script');
        scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
        vizElement.parentNode.insertBefore(scriptElement, vizElement);
    </script>
    """
    
    components.html(tableau_html, height=850, scrolling=True)
