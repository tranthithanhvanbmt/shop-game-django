Dat anh nick vao thu muc nay (jpg/jpeg/png/webp), moi anh se tao 1 AccountInventory.
Chay lenh:
..\\.venv\\Scripts\\python.exe shop_game\\manage.py seed_catalog_and_inventory --category lien-quan-mobile --source media/import_nicks

Neu muon noi dung/chinh gia theo tung anh, sua file metadata.csv trong thu muc nay.
Cot quan trong:
- filename: ten file anh (bat buoc)
- title: TAI KHOAN 01: ...
- heroes, skins, rank, win_rate
- focus_skins: cach nhau boi dau ';'
- price: gia co dinh
- price_min, price_max: khung gia (neu khong co price)
- username, password, login_method

Goi y:
- Ten file khong can theo mau dac biet.
- Co the gioi han so luong: --limit 20
- Co the doi khung gia: --min-price 450000 --max-price 600000
