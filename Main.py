import json
from pathlib import Path


def muat_basis_pengetahuan():
    lokasi_file = Path(__file__).resolve().parent / "aturan.json"

    if not lokasi_file.exists():
        raise FileNotFoundError(
            "File aturan.json tidak ditemukan. "
            "Pastikan aturan.json berada satu folder dengan Main.py."
        )

    with open(lokasi_file, "r", encoding="utf-8") as file:
        return json.load(file)


def kumpulkan_fakta(data):
    memori = set()
    fakta_awal = []

    print("=" * 70)
    print(data["judul"].upper())
    print("=" * 70)
    print("Jawablah setiap pertanyaan dengan:")
    print("  y = Ya")
    print("  t = Tidak")
    print("-" * 70)

    for nomor, pertanyaan in enumerate(data["pertanyaan"], start=1):
        while True:
            jawaban = input(
                f"{nomor}. {pertanyaan['teks']} (y/t): "
            ).strip().lower()

            if jawaban == "y":
                fakta = pertanyaan["fakta_ya"]
                memori.add(fakta)
                fakta_awal.append(fakta)
                break

            if jawaban == "t":
                fakta = pertanyaan["fakta_tidak"]
                memori.add(fakta)
                fakta_awal.append(fakta)
                break

            print("Input tidak valid. Silakan masukkan y atau t.")

    print("\nFakta awal yang diperoleh:")
    for fakta in fakta_awal:
        print(f"- {fakta}")

    return memori


def kondisi_aturan_terpenuhi(aturan, memori):
    syarat = aturan["jika"]
    mode = aturan["mode"].lower()

    if mode == "dan":
        return all(fakta in memori for fakta in syarat)

    if mode == "atau":
        return any(fakta in memori for fakta in syarat)

    raise ValueError(
        f"Mode aturan '{aturan['mode']}' pada {aturan['id']} tidak dikenal."
    )


def jalankan_forward_chaining(data, memori):
    derivasi = {}
    kesimpulan = []
    nomor_siklus = 1

    print("\n" + "=" * 70)
    print("PROSES INFERENSI FORWARD CHAINING")
    print("=" * 70)

    while True:
        ada_aturan_dijalankan = False

        for aturan in data["aturan"]:
            hasil = aturan["maka"]

            if hasil in memori:
                continue

            if kondisi_aturan_terpenuhi(aturan, memori):
                memori.add(hasil)
                derivasi[hasil] = aturan
                ada_aturan_dijalankan = True

                print(
                    f"Siklus {nomor_siklus}: "
                    f"{aturan['id']} menghasilkan -> {hasil}"
                )

                nomor_siklus += 1

                if hasil in data["kesimpulan_akhir"]:
                    kesimpulan.append(hasil)

                break

        if not ada_aturan_dijalankan:
            print("Tidak ada aturan baru yang terpenuhi.")
            print("Proses inferensi selesai.")
            break

    return kesimpulan, derivasi


def tampilkan_alasan(fakta, derivasi, tingkat=1, sudah_ditampilkan=None):
    if sudah_ditampilkan is None:
        sudah_ditampilkan = set()

    if fakta in sudah_ditampilkan:
        return

    aturan = derivasi.get(fakta)

    if aturan is None:
        print(f"{'  ' * tingkat}- Fakta awal: {fakta}")
        return

    sudah_ditampilkan.add(fakta)
    indentasi = "  " * tingkat
    daftar_syarat = " dan ".join(aturan["jika"]) if aturan["mode"] == "dan" else " atau ".join(aturan["jika"])

    print(f"{indentasi}- Aturan {aturan['id']}: {fakta}")
    print(f"{indentasi}  Syarat: {daftar_syarat}")

    for syarat in aturan["jika"]:
        tampilkan_alasan(
            syarat,
            derivasi,
            tingkat + 1,
            sudah_ditampilkan
        )


def tampilkan_hasil(data, kesimpulan, derivasi):
    print("\n" + "=" * 70)
    print("HASIL KESIMPULAN")
    print("=" * 70)

    if not kesimpulan:
        print("Kesimpulan: Belum dapat ditentukan.")
        print(
            "Alasan: Fakta yang diberikan belum memenuhi "
            "aturan untuk menghasilkan kesimpulan akhir."
        )
    else:
        for hasil in kesimpulan:
            print(f"Kesimpulan: {hasil}")
            print("Alasan/jejak aturan:")
            tampilkan_alasan(hasil, derivasi)
            print()

    print("-" * 70)
    print("CATATAN BATAS KEBERLAKUAN SISTEM")
    print(data["batas"])
    print("-" * 70)


def main():
    try:
        data = muat_basis_pengetahuan()
        memori = kumpulkan_fakta(data)
        kesimpulan, derivasi = jalankan_forward_chaining(data, memori)
        tampilkan_hasil(data, kesimpulan, derivasi)

    except FileNotFoundError as error:
        print(f"Kesalahan: {error}")

    except json.JSONDecodeError:
        print(
            "Kesalahan: Format file aturan.json tidak valid. "
            "Periksa tanda kurung, koma, dan tanda kutip pada JSON."
        )

    except KeyError as error:
        print(
            f"Kesalahan: Data pada aturan.json tidak lengkap. "
            f"Bagian yang tidak ditemukan: {error}"
        )

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")


if __name__ == "__main__":
    main()
