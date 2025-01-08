from flask import Flask, render_template, request
import os
import requests
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree, parse
import xml.dom.minidom

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/save_metadata', methods=['POST'])
def save_metadata():
    # Formdan gelen verileri al
    kaynak_id = request.form['kaynakID']
    kaynak_adi = request.form['kaynakAdi']
    kaynak_detay = request.form['kaynakDetay']
    kaynak_url = request.form['kaynakURL']
    kaynak_zaman = request.form['kaynakZamanDamgasi']

    # XML dosyasını kontrol et ve oluştur ya da yükle
    xml_file_path = 'reports/metadata.xml'
    if not os.path.exists('reports'):
        os.mkdir('reports')

    if os.path.exists(xml_file_path):
        tree = parse(xml_file_path)
        root = tree.getroot()
    else:
        root = Element('WebKaynaklar')

    # Yeni kayıt ekle
    kaynak = SubElement(root, 'WebKaynak')
    SubElement(kaynak, 'KaynakID').text = kaynak_id
    SubElement(kaynak, 'KaynakAdi').text = kaynak_adi
    SubElement(kaynak, 'KaynakDetay').text = kaynak_detay
    SubElement(kaynak, 'KaynakURL').text = kaynak_url
    SubElement(kaynak, 'KaynakZamanDamgasi').text = kaynak_zaman

    # XML dosyasını kaydet
    tree = ElementTree(root)
    with open(xml_file_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

    # URL erişilebilirlik kontrolü ve TXT dosyasına kaydetme
    txt_file_path = 'reports/url_status.txt'
    try:
        response = requests.get(kaynak_url, timeout=5)
        status = 'Erişilebilir' if response.status_code == 200 else 'Erişilemez'
    except requests.RequestException:
        status = 'Erişilemez'

    with open(txt_file_path, 'a', encoding='utf-8') as f:
        f.write(f"KaynakID: {kaynak_id}, URL: {kaynak_url}, Durum: {status}\n")

    return f"XML dosyasına kayıt eklendi ve URL durumu kaydedildi. XML dosyası: {xml_file_path}, TXT dosyası: {txt_file_path}"

if __name__ == '__main__':
    app.run(debug=True)
