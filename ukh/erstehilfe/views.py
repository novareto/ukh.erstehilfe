# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de
#

import grok
import uvcsite
import requests
import base64
from .components import ErsteHilfe
from .resources import remote, main
from uvcsite.interfaces import IMyHomeFolder
from zope.interface import implementer
from zope.file.download import bodyIterator
from zope.publisher.interfaces.http import IResult
from StringIO import StringIO

grok.templatedir('templates')


@implementer(IResult)
class DownloadResult(object):

    def __init__(self, context):
        self._iter = bodyIterator(iter(context))

    def __iter__(self):
        return self._iter


class ErsteHilfeExternalPDF(grok.View):
    grok.name('pdf')
    grok.context(ErsteHilfe)

    def update(self):
        um = self.request.principal.getUM()
        user_obj = um.getUser(self.request.principal.id)
        az = user_obj['az']
        if az == "00":
            az = "eh"
        user = "%s-%s" %(user_obj['mnr'], az)
        print user
        password = user_obj['passwort'] 
        remote = requests.get(
            'http://10.64.53.10:9955/pdf',
            auth=(user, password), params=self.request.form)

        if not remote.status_code == 200:
            raise NotImplementedError("Couldn't fetch file.")
        self.response.setHeader(
            'Content-Disposition',
            'attachment; filename="erstehilfeexternal.pdf"')

        self.data = pdfFile = StringIO(remote.content)
        self.response.setHeader('Content-Type', 'application/pdf')

    def render(self):
        return DownloadResult(self.data)


class ErsteHilfeExternal(uvcsite.Page):
    grok.context(ErsteHilfe)
    grok.name('index')

    def update(self):
        main.need()
        um = self.request.principal.getUM()
        user_obj = um.getUser(self.request.principal.id)
        user = user_obj['mnr'] 
        password = user_obj['passwort'] 
        self.basic = base64.b64encode("%s:%s" % (user, password))
        remote = requests.get(
            'http://10.64.53.10:9955/external',
            auth=(user, password))
        self.remote = remote.text
        #print remote
        #self.remote = remote.text.replace(
        #        'href="http://10.64.53.10:9955/pdf"', 'href="' + self.url(self.context) + "/'erstehilfeexternal-pdf" )
        #print self.remote
        self.remote = self.remote.replace(u'<h1> Willkommen im Erste-Hilfe-Portal der Unfallkasse Hessen</h1>',
                                          u'')
        self.remote = self.remote.replace(u'<h3><u> Weitere Informationen zur Ersten Hilfe erhalten Sie hier.</u></h3>',
                                          u'<p><u> Weitere Informationen zur Ersten Hilfe erhalten Sie auf ukh.de</u></p>')
        self.remote = self.remote.replace(u'<h1 class="lead"> Antrag auf Kostenübernahme für Erste-Hilfe-Lehrgänge </h1>',
                                          u'<h2> Antrag auf Kostenübernahme für Erste-Hilfe-Lehrgänge </h2>')
        self.remote = self.remote.replace(u'<div class="well">',
                                          u'<div>')
        self.remote = self.remote.replace(u'<p> Sie haben die Möglichkeit Ihre Berechtigungsscheine nun herunterzuladen. </p>',
                                          u'</br>')
        #self.remote = self.remote.replace(u'<a href="http://10.64.53.10:9955/pdf"><h3><u> Alle Berechtigungsscheine Downloaden </u></h3></a>',
        #                                  u'</br>')
        self.remote = self.remote.replace(
            'href="http://10.64.53.10:9955/', 'href="' + self.url(self.context) + '/')

    def render(self):
        remote.need()
        wrapper = """<div id="remote-form" rel="%s">%s</div>""" 
        return wrapper % (self.basic, self.remote)


class ErsteHilfeKontakt(grok.Viewlet):
    grok.context(ErsteHilfe)
    grok.view(ErsteHilfeExternal)
    grok.viewletmanager(uvcsite.IAboveContent)

    def render(self):
        return '<a href="%s" class="btn pull-right"> Kontakt </a>' % self.view.url(self.context, 'kontakt') 


from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
import grokcore.component


@grokcore.component.provider(IContextSourceBinder)
def voc_subject(context):
    rc = [
        SimpleTerm(u'',
                   u'',
                   u''),
        SimpleTerm(u'Berechtigungsscheine',
                   u'Berechtigungsscheine',
                   u'Berechtigungsscheine'),
        SimpleTerm(u'Lehrgangsteilnahme',
                   u'Lehrgangsteilnahme',
                   u'Lehrgangsteilnahme'),
        SimpleTerm(u'Rechnung',
                   u'Rechnung',
                   u'Rechnung'),
        SimpleTerm(u'Sonstiges',
                   u'Sonstiges',
                   u'Sonstiges'),
    ]
    return SimpleVocabulary(rc)


class IKontakt(Interface):

    betreff = schema.Choice(
        title=u'Betreff',
        source=voc_subject,
        )

    text = schema.Text(
        title=u'Nachricht'
        )


MT = u"""Der Erste-Hilfe-Benutzer

%s

%s
%s


bittet um Kontaktaufnahme zum Thema: %s

Der Benutzer hat folgende Nachricht hinterlassen:

%s


Folgende Kontaktdaten stehen zur Verfügung:

%s
%s
%s
"""


class Kontakt(uvcsite.Form):
    grok.context(ErsteHilfe)

    fields = uvcsite.Fields(IKontakt)

    @uvcsite.action('Abbrechen')
    def handle_cancel(self):
        self.flash(u'Die Aktion wurde abgebrochen.')
        self.redirect(self.application_url())

    @uvcsite.action('Absenden')
    def handle_send(self):
        data, errors = self.extractData()
        if errors:
            return
        um = self.request.principal.getUM()
        acu = um.getUser(self.request.principal.id)
        adr = self.request.principal.getAdresse()
        from uvcsite.utils.mail import send_mail
        print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
        print acu
        print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
        print adr
        print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
        adrname = adr['iknam1'].strip() + ' ' + adr['iknam2'].strip() + ' ' + adr['iknam3'].strip()
        adrstrasse = adr['ikstr'].strip() + ' ' + str(adr['ikhnr']).strip()
        adrplzort = str(adr['ikhplz']).strip() + ' ' + adr['ikhort'].strip()
        acuname = acu['vname'].strip() + ' ' + acu['nname'].strip()
        acutel = acu['vwhl'].strip() + ' ' + acu['tlnr'].strip()
        acumail = acu['email'].strip()
        text = MT % (adrname, adrstrasse, adrplzort, data[u'betreff'], data[u'text'], acuname, acutel, acumail)
        send_mail('extranet@ukh.de', ('portal-erste-hilfe@ukh.de',), u"Kontaktformular Erste Hilfe", body=text)
        #send_mail('extranet@ukh.de', ('m.seibert@ukh.de',), u"Kontaktformular Erste Hilfe", body=text)
        self.flash(u'Ihre Nachricht wurde an die Unfallkasse Hessen gesendet.')
        self.redirect(self.application_url())
