import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def plot_histogram(data, bins, xlabel, ylabel, title):
    plt.hist(data, bins=bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    st.pyplot()

def main():
    st.title('Histograma com Streamlit')

    # Gerando alguns dados aleatórios para o histograma
    data = np.random.randn(1000)

    # Configurações do histograma
    bins = st.slider('Número de bins:', min_value=1, max_value=100, value=20)
    xlabel = st.text_input('Rótulo do eixo X:', value='Valores')
    ylabel = st.text_input('Rótulo do eixo Y:', value='Frequência')
    title = st.text_input('Título:', value='Histograma')

    # Plotando o histograma
    plot_histogram(data, bins, xlabel, ylabel, title)

if __name__ == "__main__":
    main()
