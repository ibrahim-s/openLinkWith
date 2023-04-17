# Bağlantıyı Şununla Aç #

Yazarlar: İbrahim Hamadeh, Cary Rowen ve Belala Toufik.  
NVDA uyumluluğu: 2018.3 ve sonrası.  
[Sürüm 2.9'u İndirin][1]  

Bu eklenti, seçili metinden veya panoya kopyalanmış metinden bağlantıları ayıklamak için kullanılır.  
Bulunan bağlantıları, açtığı iletişim kutusunda bir listede gösterir ve bilgisayarımızda birden fazla tarayıcı varsa istediğimiz bir tarayıcı ile açabilmemize imkan verir.  

## kullanım:

*	İlk önce, girdi hareketleri iletişim kutusu aracılığıyla eklenti için bir kısayol atamamız gerekir.
*	Bunun için, NVDA Menüsü/Tercihler/Girdi Hareketleri içerisinde Bağlantıyı şununla aç kategorisine gitmek gerekir.
*	Orada atanmamış üç hareket bulunur.
	1.	Seçili metnin içinde ki bağlantıları görüntülemek için bir hareket.
	2.	Pano metnindeki bağlantıları görüntülemek için bir hareket.
	3.	Son söylenen metindeki bağlantıları göster.
*	Artık, seçili metinden veya panodaki metinden bağlantı alma ve görüntüleme seçeneğimiz var.
*	Bağlantıları almak istediğimizde, belirlediğimiz kısayol tuşlarına basmamız gerekir.
*	varsa, bağlantılar bir iletişim kutusundaki liste alaında görüntülenecektir.
*	Bağlantıyı seçtikten sonra varsayılan tarayıcıyla açmak istiyorsak enter tuşuna basmamız yeterli olur.
*	aksi takdirde, açmak istediğimiz tarayıcıya gitmek ve enter tuşuna basmak gerekir.
*	Bir bağlantıyı etkinleştirdikten sonra diyaloğu kapatma seçeneğimiz olduğunu unutmamalıyız. Bunu tercihler menüsündeki Bağlantıyı şununla aç ayarları iletişim kutusundan ayarlayabiliriz.

## Köprü menüsü:

Diyelim ki bir tarayıcıdayız ve bir bağlantı bulduk, onu başka bir tarayıcıda açmak istiyoruz.  

Ya da bir mesaj okuyoruz ve içinde bir bağlantı var, onu belirli bir tarayıcıyla (varsayılan değil) açmak istiyoruz, bu durumda ne yapmalıyız?  

İşte harika Köprü menüsü özelliği geliyor, köprü menüsünün (Alt +/) hareketine basıyoruz. Bağlantıyı makinemizdeki birkaç tarayıcıyla açma seçeneği sunan bir menü açılacaktır.  

Çoğu zaman, bir mesajı okurken bir github bağlantısıyla karşılaşıyorum, onunla github'da oturum açtığım tarayıcı Chrome'dur, varsayılan tarayıcım Firefox'tur ve soruna tepki vermek için bağlantıyı Chrome ile açmam gerekir. bağlantı. köprü menüsü, varsayılan tarayıcı olmasa bile, zaten oturum açmış olduğum tarayıcıyla github'a gitmeme yardımcı olabilir.  

Alt+/ varsayılan harekettir. Ancak bunu her zaman NVDA menüsü/Tercihler/Girdi hareketleri/Bağlantıyı şununla aç aracılığıyla değiştirebiliriz.

## 2.9 için değişiklikler: ##

*	Bağlantıyı diğer tarayıcılarla açma seçeneği sunmak için köprü menüsü özelliği eklendi.
*	Bir bağlantının üzerinde durun ve Alt+/ hareketine basın
*	Bağlantıyı makinenizdeki diğer tarayıcılarla açma seçeneği sunan bir menü açılır.
*	Menüyü kapatmak için escape tuşuna basabilir veya bağlantıyı doğrudan onunla açmak için tarayıcılardan herhangi birine girebilirsiniz.

## 2.8 için değişiklikler: ##
*	Eklenti şablonu güncellendi.
*	Eklenti apisi, 2023.1 ile uyumlu hale getirildi.

## 2.7 için değişiklikler ##

*	Artık, son konuşulan metinden bağlantıları çıkarabilirsiniz.
*	Metinde yalnızca bir bağlantı olduğunda, doğrudan varsayılan tarayıcıyla açıp açmamaya karar vermek için ayarlar panelindeki seçenekleri kullanabilirsiniz.
*	Metinde bulunan bağlantılar ayıklanınca, birden fazla aynı bağlantı varsa fazlasıtemizlenir.

## 2.6 için değişiklikler ##

*	Eklenti için Türkçe çeviri eklendi.

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

[1]: https://github.com/ibrahim-s/openLinkWith/releases/download/v2.9/openLinkWith-2.9.nvda-addon
