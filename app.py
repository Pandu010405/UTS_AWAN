from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Tambahkan kunci 'id' agar setiap data punya identitas unik
laporan_data = [
    {"id": 1, "nama": "Pandu", "status": "Sehat", "catatan": "Aman terkendali"},
    {"id": 2, "nama": "Satriajati", "status": "Siaga", "catatan": "Butuh vitamin"}
]
next_id = 3 # Counter sederhana untuk ID selanjutnya

@app.route('/')
def index():
    return render_template('index.html', laporan=laporan_data)

# Route CREATE (Tambah Data)
@app.route('/api/lapor', methods=['POST'])
def lapor():
    global next_id
    data = request.json
    
    if not data.get('nama') or not data.get('status'):
        return jsonify({"message": "Nama dan Status wajib diisi!"}), 400
        
    laporan_data.append({
        "id": next_id,
        "nama": data.get('nama'),
        "status": data.get('status'),
        "catatan": data.get('catatan')
    })
    next_id += 1
    return jsonify({"message": "Data berhasil disimpan!"}), 201

# Route UPDATE (Edit Data)
@app.route('/api/lapor/<int:item_id>', methods=['PUT'])
def update_lapor(item_id):
    data = request.json
    for item in laporan_data:
        if item['id'] == item_id:
            item['nama'] = data.get('nama', item['nama'])
            item['status'] = data.get('status', item['status'])
            item['catatan'] = data.get('catatan', item['catatan'])
            return jsonify({"message": "Data diupdate!"}), 200
            
    return jsonify({"message": "Data tidak ditemukan!"}), 404

# Route DELETE (Hapus Data)
@app.route('/api/lapor/<int:item_id>', methods=['DELETE'])
def delete_lapor(item_id):
    global laporan_data
    # Filter array untuk membuang data yang ID-nya cocok
    laporan_data = [item for item in laporan_data if item['id'] != item_id]
    return jsonify({"message": "Data dihapus!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)