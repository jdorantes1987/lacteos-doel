import os
import webbrowser 

from jinja2 import Template

html = open(os.getcwd() + "\\files\\templates\\edo_cta.html", encoding='utf-8').read()

class ReporteEstadoCuenta:
    def __init__(self):
        # Iniciamos el template con el HTML
        self.template = Template(html)

    def reder_and_open_data(self, encabezados, movimientos, nombre_file):
        # Generamos el HTML con los datos de nuestro comprobante
        template_html = self.template.render(data=encabezados,
                                             movimientos=movimientos)
        filename = os.getcwd() + f'\\files\\edos_cta\\{nombre_file}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template_html)
            f.close
            rdFile = webbrowser.open(filename)  #Full path to your file
        
        
    
    