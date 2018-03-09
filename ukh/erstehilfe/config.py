
import grok
import uvcsite

class ErsteHilfePR(uvcsite.ProductRegistration):
    grok.name('ErsteHilfe')
    grok.title('ErsteHilfe')
    grok.description('Hess Gis Lorem Ipsoum')
    uvcsite.productfolder('ukh.erstehilfe.components.ErsteHilfe')
