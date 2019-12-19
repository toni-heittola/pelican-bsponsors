# -*- coding: utf-8 -*-
"""
Sponsors listings -- BSPONSORS
================================
Author: Toni Heittola (toni.heittola@gmail.com)

"""

import os
import logging
import copy
from bs4 import BeautifulSoup
from jinja2 import Template
from pelican import signals, contents
import yaml
import collections
from io import open

logger = logging.getLogger(__name__)
__version__ = '0.1.0'

bsponsors_default_settings = {
    'panel-color': 'panel-default',
    'header': 'Sponsors',
    'mode': 'panel',
    'template': {
        'panel': """
            <div class="panel {{ panel_color }}">
              {% if header %}
              <div class="panel-heading">
                <h3 class="panel-title">{{header}}</h3>
              </div>
              {% endif %}
              <table class="table bsponsors-container">
              {{list}}
              </table>
            </div>
        """,
        'list': """
            {% if header %}<h3 class="section-heading text-center">{{header}}</h3>{% endif %}
            <div class="list-group bsponsors-container">
                <div class="row">
                {{list}}
                </div>
            </div>
        """},
    'item-template': {
        'panel': """
            <tr>
                <td class="{{item_css}}">
                    {% if homepage %}
                    <a href="{{homepage}}" target="_blank">
                    {% endif %}
                    {% if logo %}
                    <img class="img img-responsive" style="margin-left: auto;margin-right: auto;max-height:160px;" src="{{site_url}}/{{ logo }}" alt="{{name}}">
                    {% endif %}
                    {% if title %}
                    <p class="text-muted text-center">{{title}}</p>
                    {% endif %}
                    {% if homepage %}
                    </a>
                    {% endif %}
                </td>
            </tr>
        """,
        'list': """
            <div class="col-md-6 col-xs-12">
                <div class="row list-group-item-" style="padding-bottom:0.5em;">
                    {% if logo %}
                    <div class="col-md-2 col-xs-2">
                        <img class="img img-responsive" style="margin-left: auto;margin-right: auto;max-height:80px;" src="{{site_url}}/{{ logo }}" alt="{{name}}">
                    </div>
                    {% endif %}
                </div>
            </div>
        """},
    'sponsor-item-template': """
        {% if homepage %}
        <a href="{{homepage}}" target="_blank">
        {% endif %}
        {% if logo %}
        <img class="img img-responsive" style="margin-left: auto;margin-right: auto;" src="{{site_url}}/{{ logo }}" alt="{{name}}">
        {% endif %}
        {% if title %}
        <p class="text-muted text-center">{{title}}</p>
        {% endif %}
        {% if homepage %}
        </a>
        {% endif %}
    """,
    'data-source': None,
    'set': None,
    'show': False,
    'template-variable': False,
    'sponsor-name': None,
    'sort': False,
    'fields': '',
    'site-url': '',
    'debug_processing': False
}

bsponsors_settings = copy.deepcopy(bsponsors_default_settings)


def load_sponsors_registry(source):
    """

    :param source: filename of the data file
    :return: sponsors registry
    """

    if source and os.path.isfile(source):
        try:
            from distutils.version import LooseVersion
            if LooseVersion(str(yaml.__version__)) >= "5.1":
                with open(source, 'r', encoding='utf-8') as field:
                    sponsors_registry = yaml.load(field, Loader=yaml.FullLoader)
            else:
                with open(source, 'r', encoding='utf-8') as field:
                    sponsors_registry = yaml.load(field)

            if 'data' in sponsors_registry:
                sponsors_registry = sponsors_registry['data']
            sponsors_data = collections.OrderedDict()
            set_data = collections.OrderedDict()
            if 'sponsors' in sponsors_registry:
                for item in sponsors_registry['sponsors']:
                    for field in item:
                        if field.endswith('_list'):
                            if not isinstance(item[field], list):
                                item[field] = [x.strip() for x in item[field].split(';')]

                            field_list = []
                            for i in item[field]:
                                parts = [x.strip() for x in i.split(',')]
                                if len(parts) == 2:
                                    field_list.append('<a class="text" href="' + parts[1] + '">' + parts[0] + '</a>')
                                else:
                                    field_list.append(parts[0])
                            item[field] = ', '.join(field_list)
                    sponsors_data[item['name'].lower()] = item

            if 'sets' in sponsors_registry:
                set_data = collections.OrderedDict()
                for set in sponsors_registry['sets']:
                    set_dict = collections.OrderedDict()
                    for item in sponsors_registry['sets'][set]:
                        data = copy.deepcopy(sponsors_data[item['name'].lower()])
                        data.update(item)
                        item.update(data)
                        for field in item:
                            if field.endswith('_list'):
                                if not isinstance(item[field], list):
                                    item[field] = [x.strip() for x in item[field].split(';')]

                                field_list = []
                                for i in item[field]:
                                    parts = [x.strip() for x in i.split(',')]
                                    if len(parts) == 2:
                                        field_list.append('<a class="text" href="' + parts[1] + '">' + parts[0] + '</a>')
                                    else:
                                        field_list.append(parts[0])

                                item[field] = ', '.join(field_list)
                        set_dict[item['name'].lower()] = item
                    set_data[set] = set_dict
            return {
                'sponsors': sponsors_data,
                'sets': set_data
            }

        except ValueError:
            logger.warn('`pelican-bsponsors` failed to load file [' + str(source) + ']')
            return False

    else:
        logger.warn('`pelican-bsponsors` failed to load file [' + str(source) + ']')
        return False


def get_attribute(attrs, name, default=None):
    """
    Get div attribute
    :param attrs: attribute dict
    :param name: name field
    :param default: default value
    :return: value
    """

    if 'data-'+name in attrs:
        return attrs['data-'+name]
    else:
        return default


def generate_sponsor_card(settings):
    """
    Generate individual sponsor card

    :param settings: settings dict
    :return: html content
    """

    sponsor_registry = load_sponsors_registry(source=settings['data-source'])

    if sponsor_registry:

        if settings['set'] and 'sets' in sponsor_registry and settings['set'] in sponsor_registry['sets']:
            if settings['sponsor-name'].lower() in sponsor_registry['sets'][settings['set']]:
                sponsor_data = sponsor_registry['sets'][settings['set']][settings['sponsor-name'].lower()]
            else:
                logger.warn(
                    '`pelican-bsponsors` sponsor name [{name}] was not found'.format(
                        name=settings['sponsor-name']
                    ))
                return ''
        else:
            if settings['sponsor-name'].lower() in sponsor_registry['sponsors']:
                sponsor_data = sponsor_registry['sponsors'][settings['sponsor-name'].lower()]
            else:
                logger.warn(
                    '`pelican-bsponsors` sponsor name [{name}] was not found'.format(
                        name=settings['sponsor-name']
                    ))
                return ''

        valid_fields = [u'name', u'homepage', u'logo', u'title']  # default fields
        valid_fields += settings['fields']  # user defined fields

        filtered_fields = {}
        for field in sponsor_data:
            if field in valid_fields:
                filtered_fields[field] = sponsor_data[field]
            else:
                filtered_fields[field] = None

        template = Template(settings['sponsor-item-template'].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))

        filtered_fields['site_url'] = settings['site-url']
        html = BeautifulSoup(template.render(**filtered_fields), "html.parser")
        return html
    else:
        return ''


def generate_listing(settings):
    """
    Generate sponsors listing

    :param settings: settings dict
    :return: html content
    """

    sponsors_registry = load_sponsors_registry(source=settings['data-source'])
    if sponsors_registry and 'sponsors' in sponsors_registry and sponsors_registry['sponsors']:
        if 'sets' in sponsors_registry and settings['set'] in sponsors_registry['sets']:
            sponsors = sponsors_registry['sets'][settings['set']]
        else:
            sponsors = sponsors_registry['sponsors']

        if settings['sort']:
            sponsors = collections.OrderedDict(sorted(sponsors.items()))

        html = "\n"
        main_highlight = False
        for sponsor_key, sponsor in sponsors.items():
            html += generate_listing_item(sponsor=sponsor, settings=settings) + "\n"

        html += "\n"

        template = Template(settings['template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))

        return BeautifulSoup(template.render(list=html,
                                             header=settings['header'],
                                             site_url=settings['site-url'],
                                             panel_color=settings['panel-color'],), "html.parser")
    else:
        return ''


def generate_listing_item(sponsor, settings, main_highlight=False):
    """

    Generate sponsor in listing

    :param sponsor: sponsor data
    :param settings: settings dict
    :return: html content
    """

    if main_highlight:
        if settings['mode'] == 'panel':
            if 'main' in sponsor and sponsor['main']:
                item_css = 'active'
            else:
                item_css = ''
        else:
            if 'main' in sponsor and sponsor['main']:
                item_css = ''
            else:
                item_css = 'text-muted'
    else:
        item_css = ''

    valid_fields = [u'name', u'homepage', u'logo', u'title']  # default fields
    valid_fields += settings['fields']          # user defined fields

    filtered_fields = {}
    for field in sponsor:
        if field in valid_fields:
            filtered_fields[field] = sponsor[field]
        else:
            filtered_fields[field] = None

    template = Template(settings['item-template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    filtered_fields['site_url'] = settings['site-url']
    filtered_fields['item_css'] = item_css

    html = BeautifulSoup(template.render(**filtered_fields), "html.parser")
    return html.decode()


def bsponsors(content):
    """
    Main processing

    """

    if isinstance(content, contents.Static):
        return

    soup = BeautifulSoup(content._content, 'html.parser')

    # Template variable
    if bsponsors_settings['template-variable']:
        # We have page variable set
        bsponsors_settings['show'] = True
        div_html = generate_listing(settings=bsponsors_settings)
        if div_html:
            content.bsponsors = div_html.decode()
    else:
        content.bsponsors = None

    # bsponsors divs
    bsponsors_divs = soup.find_all('div', class_='bsponsors')
    bsponsor_item_divs = soup.find_all('div', class_='bsponsor-item')

    if bsponsors_divs:
        if bsponsors_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='bsponsor',
                title=content.title,
                div_count=len(bsponsors_divs)
            ))

        bsponsors_settings['show'] = True
        for bsponsor_div in bsponsors_divs:
            # We have div in the page
            settings = copy.deepcopy(bsponsors_settings)
            settings['data-source'] = get_attribute(bsponsor_div.attrs, 'source', bsponsors_settings['data-source'])
            settings['set'] = get_attribute(bsponsor_div.attrs, 'set', bsponsors_settings['set'])
            settings['template'] = get_attribute(bsponsor_div.attrs, 'template', bsponsors_settings['template'])
            settings['item-template'] = get_attribute(bsponsor_div.attrs, 'item-template', bsponsors_settings['item-template'])
            settings['mode'] = get_attribute(bsponsor_div.attrs, 'mode', bsponsors_settings['mode'])
            settings['header'] = get_attribute(bsponsor_div.attrs, 'header', bsponsors_settings['header'])
            settings['panel-color'] = get_attribute(bsponsor_div.attrs, 'panel-color', bsponsors_settings['panel-color'])
            settings['fields'] = get_attribute(bsponsor_div.attrs, 'fields', bsponsors_settings['fields'])
            settings['fields'] = [x.strip() for x in settings['fields'].split(',')]
            if not isinstance(settings['fields'], list):
                settings['fields'] = [x.strip() for x in settings['fields'].split(',')]
            settings['sort'] = get_attribute(bsponsor_div.attrs, 'sort', bsponsors_settings['sort'])
            if settings['sort'] == 'True' or settings['sort'] == 'true':
                settings['sort'] = True
            else:
                settings['sort'] = False

            div_html = generate_listing(settings=settings)
            if div_html:
                bsponsor_div.replaceWith(div_html)

    # bsponsor card divs
    if bsponsor_item_divs:
        if bsponsors_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='bsponsor-item',
                title=content.title,
                div_count=len(bsponsor_item_divs)
            ))

        bsponsors_settings['show'] = True
        for bsponsor_card_div in bsponsor_item_divs:
            # We have div in the page
            settings = copy.deepcopy(bsponsors_settings)
            settings['data-source'] = get_attribute(bsponsor_card_div.attrs, 'source', bsponsors_settings['data-source'])
            settings['set'] = get_attribute(bsponsor_card_div.attrs, 'set', bsponsors_settings['set'])
            settings['template'] = get_attribute(bsponsor_card_div.attrs, 'template', bsponsors_settings['template'])
            settings['item-template'] = get_attribute(bsponsor_card_div.attrs, 'item-template', bsponsors_settings['item-template'])
            settings['mode'] = get_attribute(bsponsor_card_div.attrs, 'mode', bsponsors_settings['mode'])
            settings['header'] = get_attribute(bsponsor_card_div.attrs, 'header', bsponsors_settings['header'])
            settings['panel-color'] = get_attribute(bsponsor_card_div.attrs, 'panel-color', bsponsors_settings['panel-color'])
            settings['sponsor-name'] = get_attribute(bsponsor_card_div.attrs, 'sponsor-name', bsponsors_settings['sponsor-name'])
            settings['fields'] = get_attribute(bsponsor_card_div.attrs, 'fields', bsponsors_settings['fields'])
            if not isinstance(settings['fields'], list):
                settings['fields'] = [x.strip() for x in settings['fields'].split(',')]

            div_html = generate_sponsor_card(settings=settings)
            if div_html:
                bsponsor_card_div.replaceWith(div_html)

    content._content = soup.decode()


def process_page_metadata(generator, metadata):
    """
    Process page metadata

    """
    global bsponsors_default_settings, bsponsors_settings
    bsponsors_settings = copy.deepcopy(bsponsors_default_settings)

    if u'bsponsors' in metadata and (metadata['bsponsors'] == 'True' or metadata['bsponsors'] == 'true'):
        bsponsors_settings['show'] = True
        bsponsors_settings['template-variable'] = True
    else:
        bsponsors_settings['show'] = False
        bsponsors_settings['template-variable'] = False

    if u'bsponsors_source' in metadata:
        bsponsors_settings['data-source'] = metadata['bsponsors_source']

    if u'bsponsors_set' in metadata:
        bsponsors_settings['set'] = metadata['bsponsors_set']

    if u'bsponsors_mode' in metadata:
        bsponsors_settings['mode'] = metadata['bsponsors_mode']

    if u'bsponsors_panel_color' in metadata:
        bsponsors_settings['panel_color'] = metadata['bsponsors_panel_color']

    if u'bsponsors_header' in metadata:
        bsponsors_settings['header'] = metadata['bsponsors_header']

    if u'bsponsors_fields' in metadata:
        bsponsors_settings['fields'] = metadata['bsponsors_fields']
        bsponsors_settings['fields'] = [x.strip() for x in bsponsors_settings['fields'].split(',')]

    if u'bpsponsors_sort' in metadata and (metadata['bsponsors_sort'] == 'True' or metadata['bsponsors_sort'] == 'true'):
        bsponsors_settings['sort'] = True


def init_default_config(pelican):
    """
    Handle settings from pelicanconf.py

    """
    global bsponsors_default_settings, bsponsors_settings

    bsponsors_default_settings['site-url'] = pelican.settings['SITEURL']

    if 'BSPONSORS_SOURCE' in pelican.settings:
        bsponsors_default_settings['data-source'] = pelican.settings['BSPONSORS_SOURCE']

    if 'BSPONSORS_TEMPLATE' in pelican.settings:
        bsponsors_default_settings['template'].update(pelican.settings['BSPONSORS_TEMPLATE'])

    if 'BSPONSORS_ITEM_TEMPLATE' in pelican.settings:
        bsponsors_default_settings['item-template'].update(pelican.settings['BSPONSORS_ITEM_TEMPLATE'])

    if 'BSPONSORS_SPONSOR_ITEM_TEMPLATE' in pelican.settings:
        bsponsors_default_settings['sponsor-item-template'] = pelican.settings['BSPONSORS_SPONSOR_ITEM_TEMPLATE']

    if 'BSPONSORS_HEADER' in pelican.settings:
        bsponsors_default_settings['header'] = pelican.settings['BSPONSORS_HEADER']

    if 'BSPONSORS_PANEL_COLOR' in pelican.settings:
        bsponsors_default_settings['panel-color'] = pelican.settings['BSPONSORS_PANEL_COLOR']

    if 'BSPONSORS_SORT' in pelican.settings:
        bsponsors_default_settings['sort'] = pelican.settings['BSPONSORS_SORT']

    if 'BSPONSORS_DEBUG_PROCESSING' in pelican.settings:
        bsponsors_default_settings['debug_processing'] = pelican.settings['BSPONSORS_DEBUG_PROCESSING']

    bsponsors_settings = copy.deepcopy(bsponsors_default_settings)


def register():
    """
    Register signals

    """

    signals.initialized.connect(init_default_config)
    signals.article_generator_context.connect(process_page_metadata)
    signals.page_generator_context.connect(process_page_metadata)

    signals.content_object_init.connect(bsponsors)
