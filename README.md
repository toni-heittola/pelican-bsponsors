Pelican-bsponsors - Sponsor listings for Pelican
===================================================

`pelican-bsponsors` is an open source Pelican plugin to produce sponsor listings from yaml data structures. The plugin is developed to be used with Markdown content and Bootstrap 3 based template. 

**Author**

Toni Heittola (toni.heittola@gmail.com), [GitHub](https://github.com/toni-heittola), [Home page](http://www.cs.tut.fi/~heittolt/)

Installation instructions
=========================

## Requirements

**bs4** is required. To ensure that all external modules are installed, run:

    pip install -r requirements.txt

**bs4** (BeautifulSoup) for parsing HTML content

    pip install beautifulsoup4

## Pelican installation

Make sure you include [Bootstrap](http://getbootstrap.com/) in your template.

Make sure the directory where the plugin was installed is set in `pelicanconf.py`. For example if you installed in `plugins/pelican-bsponsors`, add:

    PLUGIN_PATHS = ['plugins']

Enable `pelican-bsponsors` with:

    PLUGINS = ['pelican-bsponsors']

Insert sponsor list or panel into the page template:
 
    {% if page.bsponsors %}
        {{ page.bsponsors }}
    {% endif %}

Insert sponsor list or panel into the article template:

    {% if article.bsponsors %}
        {{ article.bsponsors }}
    {% endif %}

Usage
=====

Personnel listing generation is triggered for the page either by setting BPERSONNEL metadata for the content (page or article) or using `<div>` with class `bsponsors` or `bsponsor-item`. 

Layouts

- **bsponsors**, bsponsor listing  
- **bsponsor-item**, individual sponsor information card

There is two layout modes available for both of these: `panel` and `list`. 

## Sponsor registry

Registry has two parts: 
    - **`sponsors`** containing basic information of each sponsor
    - **`sets`**, list of sponsors assigned to the set and extra information to override basic information 

Example yaml-file:

    sponsors:
      - name: Sponsor 1
        homepage: http://www.test.sponsor.hompage.com
        logo: images/logo1.jpg
      - name: Sponsor 2
        homepage: http://www.test.sponsor.hompage.com
        photo: images/logo2.jpg
        title: Technical sponsor
        
    sets:
      set1:
        - name: Sponsor 1
          title: first sponsor
        - name: Sponsor 2
          title: second sponsor
      set2:
        - name: Sponsor 1                 

Fields having values in sets (other than name) will override sponsor fields. Fields ending with `_list` are converted into list of links. Format for these fields `[title1],[link1];[title2],[link2]`

The default templates support following fields:

- name
- homepage, homepage url
- logo, link logo image
- title

## Parameters

The parameters can be set in global, and content level. Globally set parameters are are first overwritten content meta data, and finally with div parameters.

### Global parameters

Parameters for the plugin can be set in `pelicanconf.py' with following parameters:

| Parameter                 | Type      | Default       | Description  |
|---------------------------|-----------|---------------|--------------|
| BSPONSORS_SOURCE          | String    |  | YAML-file to contain sponsor registry, see example format above. |
| BSPONSORS_TEMPLATE        | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BSPONSORS_ITEM_TEMPLATE   | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BSPONSORS_SPONSOR_ITEM_TEMPLATE  | Jinja2 template |  | Template for sponsor information card  |
| BSPONSORS_PANEL_COLOR          | String    | panel-primary |  CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BSPONSORS_HEADER               | String    | Content       | Header text  |
| BSPONSORS_SORT              | Boolean    | False       | Sorting of the listing based on name |

### Content wise parameters

| Parameter                 | Example value     | Description  |
|---------------------------|-----------|--------------|
| BSPONSORS                 | True      | Enable bsponsors listing for the page | 
| BSPONSORS_SOURCE         | content/data/sponsors.yaml | Sponsor registry file |
| BSPONSORS_SET            | set1 | Sponsors set used, if empty full sponsor list is used.   |
| BSPONSORS_MODE           | panel | Layout type, panel or list |
| BSPONSORS_PANEL_COLOR    | panel-info | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BSPONSORS_HEADER         | Sponsors | Header text  |
| BSPONSORS_FIELDS         |          | comma separated list of field to be shown |
| BSPONSORS_SORT           | True     | Sorting of the listing based on name |

Example:

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bsponsors: True
    bsponsors_set: set1
    bsponsors_header: Current sponsors
    
Sponsor listing is available in template in variable `page.bsponsors` or `article.bsponsors`
   
### Div wise parameters

Valid for `<div>` classes `bsponsors` and `bsponsor-item`:

| Parameter                 | Example value     | Description  |
|---------------------------|-------------|--------------|
| data-source               | content/data/sponsors.yaml | Sponsor registry file
| data-set                  | set1        | Sponsor set used, if empty full sponsor list is used.  |
| data-mode                 | panel       | Layout type, panel or list |
| data-header               | Sponsors    | Header text |
| data-panel-color          | panel-info  | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| data-fields               |             | comma separated list of field to be shown |
| data-sort                 | True        | Sorting of the listing based on name  |

Valid for `bsponsor-item`:

| Parameter                 | Example value   | Description  |
|---------------------------|-----------------|--------------|
| data-name                 | CompanyName     | Name of the sponsor to be shown |
 

Example listing:

    <div class="bsponsors" data-source="content/data/sponsors.yaml" data-set="set1"></div>
    
Example of sponsor cards   

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bsponsors_source: content/data/sponsors.yaml
    <div class="bsponsors-card" data-sponsor-name="CompanyName"></div>