# Görüntü Sahteciliği Tespiti Projesi

Bu proje, yüklenen bir görsel üzerinde görüntü sahteciliği olup olmadığını analiz etmek amacıyla geliştirilmiştir. Projede özellikle copy-move forgery yani aynı görüntü içerisinden bir bölgenin kopyalanıp başka bir yere yapıştırılması gibi sahtecilik türlerinin tespit edilmesi hedeflenmiştir.

Proje Python tabanlıdır ve web arayüzü için Flask framework’ü kullanılmıştır. Görüntü işleme işlemleri OpenCV kütüphanesi ile gerçekleştirilmiştir.

## Projenin Amacı

Günümüzde dijital görseller kolayca düzenlenebilir, değiştirilebilir veya manipüle edilebilir. Bu durum özellikle haber, güvenlik, adli bilişim ve sosyal medya alanlarında yanlış bilgi yayılımına sebep olabilir.

Bu projenin amacı, kullanıcı tarafından yüklenen bir görseli analiz ederek görsel üzerinde sahtecilik izleri olup olmadığını tespit etmektir.

## Kullanılan Teknolojiler

- Python
- Flask
- OpenCV
- NumPy
- Pillow
- HTML
- CSS
- JavaScript
- SonarQube
- Doxygen
- Graphviz

## Kullanılan Yöntemler

Projede görüntü sahteciliği tespiti için farklı görüntü işleme ve özellik çıkarım yöntemleri kullanılmıştır.

### SIFT

SIFT, görsel üzerindeki belirgin noktaları tespit etmek için kullanılan güçlü bir özellik çıkarım algoritmasıdır. Ölçek ve döndürme değişimlerine karşı dayanıklıdır.

### SURF

SURF, SIFT’e benzer şekilde görüntü üzerindeki önemli noktaları bulur. Daha hızlı çalışmasıyla bilinir.

### ORB

ORB, hızlı ve verimli çalışan bir özellik çıkarım algoritmasıdır. Gerçek zamanlı görüntü işleme uygulamalarında tercih edilebilir.

### AKAZE

AKAZE, görüntü üzerindeki yerel özellikleri tespit etmek için kullanılan modern bir algoritmadır. Özellikle karmaşık görüntülerde başarılı sonuçlar verebilir.

### AI-CNN ve AI-LSTM Yaklaşımı

Projede teorik olarak yapay zeka tabanlı yöntemler de ele alınmıştır. CNN görüntülerdeki görsel desenleri öğrenmek için, LSTM ise sıralı veri ilişkilerini modellemek için kullanılabilir.

## Proje Özellikleri

- Kullanıcıdan tek bir görsel alma
- Görseli web arayüzü üzerinden yükleme
- Görüntü üzerinde sahtecilik analizi yapma
- Şüpheli bölgeleri tespit etme
- Analiz sonucunu kullanıcıya gösterme
- Görsel işleme algoritmalarını karşılaştırmalı olarak kullanabilme
- Kod kalitesini SonarQube ile analiz etme
- Doxygen ile proje dokümantasyonu oluşturma
- Graphviz ile proje yapısını görselleştirme

## Proje Klasör Yapısı

```txt
proje2_goruntu_sahtecilik/
│
├── run.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── detectors.py
│   ├── utils.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── uploads/
│       ├── results/
│       └── style.css
```

## Kurulum

Projeyi çalıştırmadan önce bilgisayarda Python kurulu olmalıdır.

Öncelikle proje klasörüne girilir:

cd proje2_goruntu_sahtecilik

Sanal ortam oluşturulur:

python -m venv venv

Sanal ortam aktif edilir.

Windows için:

venv\Scripts\activate

Mac/Linux için:

source venv/bin/activate

Gerekli kütüphaneler yüklenir:

pip install -r requirements.txt

Eğer requirements.txt dosyası yoksa aşağıdaki kütüphaneler manuel olarak kurulabilir:

pip install flask opencv-python opencv-contrib-python numpy pillow werkzeug

## Projeyi Çalıştırma

Proje aşağıdaki komut ile çalıştırılır:

python run.py

Daha sonra tarayıcıdan şu adrese gidilir:

http://127.0.0.1:5000

## Kullanım

1. Web arayüzü açılır.
2. Kullanıcı analiz etmek istediği görseli seçer.
3. Görsel sisteme yüklenir.
4. Sistem görüntü üzerinde sahtecilik analizi yapar.
5. Sonuç ekranda gösterilir.
6. Eğer sahtecilik şüphesi varsa ilgili bölgeler işaretlenir.

## SonarQube Analizi

Projenin kod kalitesini ölçmek için SonarQube kullanılmıştır. SonarQube ile kod içerisindeki hata, güvenlik açığı, tekrar eden kod ve bakım yapılabilirlik durumları incelenmiştir.

SonarQube çalıştırmak için örnek komut:

sonar-scanner

Bu analiz sonucunda projenin kalite durumu değerlendirilmiş ve gerekli iyileştirmeler yapılmıştır.

## Doxygen Dokümantasyonu

Kod dokümantasyonu oluşturmak için Doxygen kullanılmıştır. Doxygen, proje içerisindeki fonksiyonları, sınıfları ve dosya yapılarını otomatik olarak belgelemeye yardımcı olur.

Doxygen çalıştırmak için:

doxygen Doxyfile

Oluşturulan dokümantasyon genellikle aşağıdaki klasörde yer alır:

docs/html/index.html

## Graphviz Kullanımı

Proje yapısını görselleştirmek için Graphviz kullanılmıştır. Graphviz sayesinde fonksiyonlar ve dosyalar arasındaki ilişkiler grafiksel olarak gösterilebilir.

Örnek komut:

dot -Tpng project_graph.dot -o project_graph.png

Bu komut sonucunda project_graph.png adlı görsel çıktı oluşturulur.

## Projenin Avantajları

- Kullanımı kolay web arayüzüne sahiptir.
- Tek görsel üzerinden analiz yapılabilir.
- OpenCV tabanlı görüntü işleme yöntemleri kullanılmıştır.
- Farklı algoritmalarla karşılaştırmalı analiz yapılabilir.
- Kod kalitesi SonarQube ile kontrol edilebilir.
- Doxygen ile proje dokümantasyonu oluşturulabilir.

## Projenin Sınırlılıkları

- Sahtecilik tespiti her görselde yüzde yüz kesin sonuç vermez.
- Düşük kaliteli veya çok sıkıştırılmış görsellerde tespit başarısı azalabilir.
- Çok küçük manipülasyonlar her zaman algılanamayabilir.
- Yapay zeka tabanlı yöntemlerin daha başarılı çalışması için büyük veri setlerine ihtiyaç vardır.

## Gelecek Geliştirmeler

- Daha gelişmiş yapay zeka modellerinin eklenmesi
- CNN tabanlı otomatik sahtecilik sınıflandırması
- Görseller için güven skoru hesaplama
- Birden fazla algoritmanın sonuçlarını karşılaştıran rapor ekranı
- Kullanıcıya detaylı PDF analiz raporu oluşturma
- Mobil uyumlu arayüz geliştirme

## Sonuç

Bu proje, dijital görseller üzerinde sahtecilik tespiti yapmak amacıyla geliştirilmiş bir görüntü işleme uygulamasıdır. Flask ile web tabanlı bir yapı kurulmuş, OpenCV ile görüntü analiz işlemleri gerçekleştirilmiştir.

Proje sayesinde kullanıcılar bir görsel yükleyerek sahtecilik şüphesi olup olmadığını hızlı bir şekilde analiz edebilir. Ayrıca SonarQube, Doxygen ve Graphviz gibi araçlarla proje hem kalite hem de dokümantasyon açısından desteklenmiştir.

## Geliştirici

Sevim Akdeniz

Yazılım Mühendisliği  
Görüntü İşleme ve Web Tabanlı Uygulama Projesi
