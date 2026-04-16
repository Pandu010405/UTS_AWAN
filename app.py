from dotenv import load_dotenv
load_dotenv()
import os
import boto3
import psycopg2
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Konfigurasi S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name='ap-southeast-2' # Sesuaikan jika region kamu beda (misal Sydney)
)
S3_BUCKET = os.environ.get('S3_BUCKET', 'healthtrack-pribadi-pandu')

# Fungsi Koneksi ke RDS PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME', 'health_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASS', 'Pandu0104')
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # Mengambil data dari tabel database
    cur.execute('SELECT id, nama, status, catatan, foto_url FROM laporan_kesehatan ORDER BY id DESC')
    rows = cur.fetchall()
    
    laporan_data = []
    for row in rows:
        laporan_data.append({
            "id": row[0], "nama": row[1], "status": row[2], 
            "catatan": row[3], "foto_url": row[4]
        })
    
    cur.close()
    conn.close()
    return render_template('index.html', laporan=laporan_data)

@app.route('/api/lapor', methods=['POST'])
def lapor():
    # Karena ada file, kita pakai request.form, bukan request.json
    nama = request.form.get('nama')
    status = request.form.get('status')
    catatan = request.form.get('catatan', '-')
    foto = request.files.get('foto')

    if not nama or not status:
        return jsonify({"message": "Nama dan Status wajib diisi!"}), 400

    foto_url = None
    if foto and foto.filename != '':
        # Upload ke S3
        filename = secure_filename(foto.filename)
        s3_client.upload_fileobj(
            foto, 
            S3_BUCKET, 
            filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': foto.content_type}
        )
        foto_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"

    # Simpan URL dan data ke RDS
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO laporan_kesehatan (nama, status, catatan, foto_url) VALUES (%s, %s, %s, %s)',
        (nama, status, catatan, foto_url)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data & Foto berhasil disimpan ke Cloud!"}), 201

# Route DELETE (Sama seperti sebelumnya, tapi pakai Database)
@app.route('/api/lapor/<int:item_id>', methods=['DELETE'])
def delete_lapor(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM laporan_kesehatan WHERE id = %s', (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Data dihapus dari Database!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')