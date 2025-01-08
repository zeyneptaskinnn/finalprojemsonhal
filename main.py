from flask import Flask, render_template, request, redirect, url_for
import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

app = Flask(__name__, template_folder="src/templates")

# XML dosyasını oluşturmak için kullanılacak temel fonksiyon
def create_xml_file(data, filename="metadata.xml"):
    root = ET.Element("WebResources")
    for resource in data:
        resource_element = ET.SubElement(root, "Resource")
        for key, value in resource.items():
            child = ET.SubElement(resource_element, key)
            child.text = value
    tree = ET.ElementTree(root)
    tree.write(filename)

# URL erişilebilirliğini kontrol eden fonksiyon
def check_url_availability(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Raporlama sonucu TXT dosyasına kaydedilir
def save_report(report_data, filename="report.txt"):
    with open(filename, "w") as file:
        for line in report_data:
            file.write(line + "\n")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        kaynak_id = request.form.get("kaynakID")
        kaynak_adi = request.form.get("kaynakAdi")
        kaynak_detay = request.form.get("kaynakDetay")
        kaynak_url = request.form.get("kaynakURL")
        zaman_damgasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metadata = [
            {
                "kaynakID": kaynak_id,
                "kaynakAdi": kaynak_adi,
                "kaynakDetay": kaynak_detay,
                "KaynakURL": kaynak_url,
                "kaynakZamanDamgasi": zaman_damgasi
            }
        ]

        # XML dosyasını oluştur
        create_xml_file(metadata)

        # URL erişilebilirliğini kontrol et
        is_accessible = check_url_availability(kaynak_url)
        status = "Erişilebilir" if is_accessible else "Erişilemez"

        # Raporu kaydet
        report_line = f"{zaman_damgasi} | {kaynak_adi} ({kaynak_url}) - Durum: {status}"
        save_report([report_line])

        return redirect(url_for("report"))

    return render_template("index.html")

@app.route("/report")
def report():
    try:
        with open("report.txt", "r") as file:
            report_lines = file.readlines()
    except FileNotFoundError:
        report_lines = []

    return render_template("report.html", reports=report_lines)

if __name__ == "__main__":
    app.run(debug=True)