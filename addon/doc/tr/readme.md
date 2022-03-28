# Bağlantıyı Şununla Aç #

Yazarlar: İbrahim Hamadeh, Belala Toufik.  
Katkıda bulunanlar: cary-rowen.  
NVDA uyumluluğu: 2018.3 ve sonrası.  
[Sürüm 2.5'i İndir][1]  

Bu eklenti, seçili metinden veya panoya kopyalanmış metinden bağlantıları ayıklamak için kullanılır.  
Bulunan bağlantıları, açtığı iletişim kutusunda bir listede gösterir ve bilgisayarımızda birden fazla tarayıcı varsa istediğimiz bir tarayıcı ile açabilmemize imkan verir.  

## kullanım:

*	İlk önce, girdi hareketleri iletişim kutusu aracılığıyla eklenti için bir kısayol atamamız gerekir.
*	Bunun için, NVDA Menüsü/Tercihler/Girdi Hareketleri içerisinde Bağlantıyı şununla aç kategorisine gitmek gerekir.
*	Orada atanmamış iki hareket bulunur.
	1.	Seçili metnin içinde ki bağlantıları görüntülemek için bir hareket.
	2.	Pano metnindeki bağlantıları görüntülemek için bir hareket.
*	Artık, seçili metinden veya panodaki metinden bağlantı alma ve görüntüleme seçeneğimiz var.
*	Bağlantıları almak istediğimizde, belirlediğimiz kısayol tuşlarına basmamız gerekir.
*	varsa, bağlantılar bir iletişim kutusundaki liste alaında görüntülenecektir.
*	Bağlantıyı seçtikten sonra varsayılan tarayıcıyla açmak istiyorsak enter tuşuna basmamız yeterli olur.
*	aksi takdirde, açmak istediğiniz tarayıcıya gidin ve enter tuşuna basın.
*	Bir bağlantıyı etkinleştirdikten sonra diyaloğu kapatma seçeneğiniz olduğunu unutmayın. Bunu tercihler menüsündeki openLinkWith ayarları iletişim kutusundan ayarlayabilirsiniz.

## 2.5 için değişiklikler ##

*	Eklentinin güvenli modda çalışması devre dışı bırakıldı.
*	En son eklenti API'sine uymak için 2022.1'e güncellendi.

## 2.4 için değişiklikler ##

*	Artık eklenti için atanmamış iki hareketimiz var.
*	Biri seçili metindeki bağlantıları görüntülemek için, diğeri ise pano metninde ki bağlantıları görüntülemek için.
*	En son eklenti şablon dosyaları kullanıldı.
*	Test edilen minimum ve son sürüm için manifest.ini güncellendi.

## 2.2 için değişiklikler ##
*	python3 ile uyumluluğu sağlar.

## 2.0 için değişiklikler ##

*	Artık standart tarayıcılara C sürücüsünden değil, kayıt defterinden erişiyoruz.
*	Tercihler menüsünde eklenti için bir yapılandırma ayarları iletişim kutusu eklendi. Böylece bir bağlantıyı etkinleştirdikten sonra diyaloğu kapatma seçeneğimiz var.
*	Windows10'da mevcutsa tarayıcılara Edge tarayıcı eklendi.
*	NVDA2018.2 veya sonraki sürümlere uyması için ayarlar paneli eklendi.

## 1.0 için değişiklikler ##

*	İlk Sürüm.

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/v2.5/openLinkWith-2.5.nvda-addon
