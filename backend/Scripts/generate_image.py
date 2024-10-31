import matplotlib.pyplot as plt
import io

def generate_solution_image(equation, solution):
    """
    Genera una imagen con la ecuación original y su solución usando Matplotlib
    """
    fig, ax = plt.subplots()
    ax.text(0.5, 0.8, f"Ecuación: {equation}", fontsize=12, ha='center')
    ax.text(0.5, 0.6, f"Solución: {solution}", fontsize=12, ha='center')

    # Eliminar los ejes
    ax.axis('off')

    # Guardar la imagen en un BytesIO
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight')
    img_io.seek(0)

    return img_io