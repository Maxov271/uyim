/* Uyim.uz — mock data layer.
   Har bir massiv backend API bilan 1:1 mos: /api/listings, /api/geo, /api/banks ...
   Claude Code: bu faylni API klient bilan almashtirish kifoya (window.UyimData shakli saqlanadi). */

window.UyimData = (() => {
  const CITIES = [
    { id:'tashkent', name:"Toshkent", center:[41.2995,69.2401], zoom:11 },
    { id:'samarkand', name:"Samarqand", center:[39.6542,66.9597], zoom:12 },
    { id:'bukhara', name:"Buxoro", center:[39.7747,64.4286], zoom:12 },
    { id:'andijan', name:"Andijon", center:[40.7821,72.3442], zoom:12 },
    { id:'fergana', name:"Farg'ona", center:[40.3864,71.7864], zoom:12 },
    { id:'namangan', name:"Namangan", center:[40.9983,71.6726], zoom:12 },
    { id:'nukus', name:"Nukus", center:[42.4600,59.6166], zoom:12 },
    { id:'qarshi', name:"Qarshi", center:[38.8600,65.7890], zoom:12 },
    { id:'urgench', name:"Urganch", center:[41.5500,60.6333], zoom:12 },
    { id:'termiz', name:"Termiz", center:[37.2242,67.2783], zoom:12 }
  ];

  // Toshkent tumanlari + har birida mahalla (MFY) ro'yxati — mahalla darajasidagi filtr uchun
  const DISTRICTS = [
    { id:'chilonzor', city:'tashkent', name:"Chilonzor", center:[41.2750,69.2050], ppm:1180,
      mahallas:["Qatortol","Novza","Oqqo'rg'on","Chilonzor-19","Xalqlar do'stligi"] },
    { id:'yunusobod', city:'tashkent', name:"Yunusobod", center:[41.3600,69.2890], ppm:1340,
      mahallas:["Bodomzor","Minor","Turkiston","Yunusobod-4","Shifokorlar"] },
    { id:'mirzo-ulugbek', city:'tashkent', name:"Mirzo Ulug'bek", center:[41.3300,69.3400], ppm:1210,
      mahallas:["Buyuk Ipak Yo'li","Qorasuv","Feruza","Universitet"] },
    { id:'yakkasaroy', city:'tashkent', name:"Yakkasaroy", center:[41.2830,69.2560], ppm:1450,
      mahallas:["Shota Rustaveli","Bobur","Qushbegi","Yakkasaroy markaz"] },
    { id:'shayxontohur', city:'tashkent', name:"Shayxontohur", center:[41.3200,69.2200], ppm:1260,
      mahallas:["Chorsu","Beruniy","Zarqaynar","Ko'kcha"] },
    { id:'mirobod', city:'tashkent', name:"Mirobod", center:[41.2900,69.2900], ppm:1520,
      mahallas:["Salar","Temir yo'l","Oybek","Mirobod markaz"] },
    { id:'olmazor', city:'tashkent', name:"Olmazor", center:[41.3500,69.2100], ppm:980,
      mahallas:["Qora qamish","Tinchlik","Olmazor markaz"] },
    { id:'uchtepa', city:'tashkent', name:"Uchtepa", center:[41.2900,69.1700], ppm:920,
      mahallas:["Chinobod","Xonobod","Uchtepa-6"] },
    { id:'sergeli', city:'tashkent', name:"Sergeli", center:[41.2200,69.2200], ppm:860,
      mahallas:["Sergeli-7","Yangihayot","Quruvchi"] },
    { id:'yashnobod', city:'tashkent', name:"Yashnobod", center:[41.2800,69.3300], ppm:1010,
      mahallas:["Tuzel","Parkent","Yashnobod markaz"] },
    { id:'bektemir', city:'tashkent', name:"Bektemir", center:[41.2100,69.3400], ppm:780,
      mahallas:["Bektemir markaz","Kimyogar"] }
  ];

  const DEAL_TYPES = [
    { id:'sale', label:"Sotib olish" },
    { id:'new', label:"Yangi binolar" },
    { id:'rent', label:"Uzoq muddat ijara" },
    { id:'daily', label:"Kunlik ijara" },
    { id:'commercial', label:"Tijorat" },
    { id:'land', label:"Yer uchastkasi" }
  ];

  const PROP_TYPES = ["Kvartira","Hovli uy","Tijorat","Yer uchastkasi","Ofis","Ombor"];

  const BANKS = [
    { id:'ipoteka', name:"Ipoteka Bank", rate:17.0, minDown:15, maxTerm:20, note:"Yangi bino uchun 15% boshlang'ich" },
    { id:'xalq', name:"Xalq Banki", rate:18.5, minDown:20, maxTerm:15, note:"Ikkilamchi bozor uchun ham amal qiladi" },
    { id:'qqb', name:"Qishloq Qurilish Bank", rate:16.5, minDown:25, maxTerm:20, note:"Tumanlarda qurilish uchun imtiyoz" },
    { id:'agro', name:"Agrobank", rate:19.0, minDown:20, maxTerm:12, note:"Tez ko'rib chiqish · 3 kun" },
    { id:'sqb', name:"SQB", rate:18.0, minDown:20, maxTerm:15, note:"Onlayn oldindan tasdiqlash" },
    { id:'subsidy', name:"Subsidiya (davlat dasturi)", rate:10.0, minDown:15, maxTerm:20, note:"Yosh oilalar uchun cheklangan kvota" }
  ];

  const DEVELOPERS = [
    { name:"Golden House", projects:12, city:"Toshkent" },
    { name:"Murad Buildings", projects:8, city:"Toshkent" },
    { name:"Akay Group", projects:6, city:"Toshkent" },
    { name:"NRG Group", projects:9, city:"Toshkent" },
    { name:"Orient Group", projects:5, city:"Samarqand" },
    { name:"Qurilish Trest-12", projects:4, city:"Buxoro" }
  ];

  const AGENTS = [
    { id:'a1', name:"Golden House Agency", type:'agency', verified:true, years:4, listings:18, rating:4.8, phone:"+998 90 123 45 67", tg:"@goldenhouse_uz" },
    { id:'a2', name:"Dilshod Karimov", type:'owner', verified:true, years:0, listings:1, rating:0, phone:"+998 93 555 21 09", tg:"@dilshod_uy" },
    { id:'a3', name:"Makon Realty", type:'agency', verified:true, years:6, listings:41, rating:4.6, phone:"+998 71 200 30 40", tg:"@makon_realty" },
    { id:'a4', name:"Zarnigor Yusupova", type:'owner', verified:false, years:0, listings:2, rating:0, phone:"+998 99 810 44 12", tg:"" }
  ];

  // narx — USD; sum kursi 12 700
  const RATE_UZS = 12700;

  const L = (id,deal,type,price,rooms,area,floor,floors,district,mahalla,lat,lng,o) => Object.assign({
    id, deal, type, price, rooms, area, floor, floors, district, mahalla,
    city:'tashkent', lat, lng, photos:14, year:2019, condition:"Evro ta'mir",
    agent:'a1', verified:true, top:false, hot:false, isNew:false, tg:true,
    metro:"Novza", metroMin:8, mortgage:true, created:"3 kun oldin",
    views:840, priceHistory:[ {m:"Mar", v:price*1.05}, {m:"May", v:price*1.02}, {m:"Iyl", v:price} ],
    features:["Konditsioner","Mebelli","Parking","Yopiq hovli","Internet · optika"],
    desc:"Tinch hovlida joylashgan yorug' kvartira. Oshxona jihozlangan, konditsioner va o'rnatilgan mebel qoladi. Hujjatlar tayyor — kadastr va notarial oldi-sotdiga to'liq mos."
  }, o||{});

  const LISTINGS = [
    L('l1','sale','Kvartira',82000,3,78,9,12,'chilonzor',"Qatortol",41.2762,69.2043,{ top:true, metro:"Novza", metroMin:8, views:1240 }),
    L('l2','sale','Kvartira',64500,2,54,4,9,'chilonzor',"Novza",41.2721,69.2101,{ hot:true, agent:'a2', condition:"O'rta ta'mir", views:960 }),
    L('l3','new','Kvartira',118000,4,102,7,16,'yunusobod',"Bodomzor",41.3591,69.2872,{ isNew:true, top:true, year:2026, condition:"Qurilish tugagan", agent:'a3', views:1580 }),
    L('l4','sale','Kvartira',96000,3,84,11,14,'mirzo-ulugbek',"Buyuk Ipak Yo'li",41.3312,69.3388,{ metro:"BIY", metroMin:5, views:720 }),
    L('l5','rent','Kvartira',640,2,58,3,5,'yakkasaroy',"Shota Rustaveli",41.2836,69.2564,{ metro:"Kosmonavtlar", metroMin:6, mortgage:false, views:410 }),
    L('l6','daily','Kvartira',38,1,42,2,4,'mirobod',"Oybek",41.2913,69.2887,{ mortgage:false, agent:'a3', views:290 }),
    L('l7','sale','Hovli uy',175000,5,180,1,2,'olmazor',"Tinchlik",41.3512,69.2088,{ year:2015, features:["Hovli 6 sotix","Garaj","Issiqxona","Quduq"], views:530 }),
    L('l8','new','Kvartira',72000,2,61,12,18,'sergeli',"Yangihayot",41.2214,69.2189,{ isNew:true, year:2026, agent:'a3', condition:"Oq holat", views:880 }),
    L('l9','sale','Kvartira',58000,2,50,2,4,'uchtepa',"Chinobod",41.2894,69.1712,{ verified:false, agent:'a4', condition:"Ta'mir talab", views:340 }),
    L('l10','commercial','Tijorat',240000,0,220,1,3,'shayxontohur',"Chorsu",41.3196,69.2213,{ features:["Ko'cha chizig'i","Alohida kirish","3 fazali quvvat"], views:610 }),
    L('l11','sale','Kvartira',134000,4,110,5,9,'mirobod',"Salar",41.2905,69.2921,{ top:true, agent:'a3', views:1120 }),
    L('l12','rent','Hovli uy',1200,4,150,1,2,'yunusobod',"Minor",41.3628,69.2841,{ mortgage:false, views:250 }),
    L('l13','land','Yer uchastkasi',45000,0,600,0,0,'yashnobod',"Parkent",41.2814,69.3312,{ features:["8 sotix","Kadastr tayyor","Yo'l chizig'i"], mortgage:false, views:300 }),
    L('l14','new','Kvartira',89000,3,76,3,16,'chilonzor',"Chilonzor-19",41.2788,69.1998,{ isNew:true, year:2025, hot:true, views:1010 })
  ];

  const SAVED_SEARCHES = [
    { id:'s1', title:"Chilonzor · 2–3 xona · 40–120 ming $", meta:"12 yangi e'lon · bugun", on:true, tg:true },
    { id:'s2', title:"Yunusobod · yangi bino · ipoteka bilan", meta:"4 yangi e'lon · kecha", on:true, tg:true },
    { id:'s3', title:"Samarqand · kunlik ijara · markaz", meta:"Yangilik yo'q", on:false, tg:false }
  ];

  const DISTRICT_STATS = DISTRICTS.slice(0,8).map((d,i) => ({
    district:d.name, ppm:d.ppm, delta:[+4.2,+6.1,+2.8,+1.4,+3.3,-0.7,+5.0,+2.1][i], supply:[1240,860,910,430,700,520,380,290][i]
  }));

  const NOTIFICATIONS = [
    { icon:'ph-bell-ringing', text:"“Chilonzor · 2–3 xona” qidiruvi bo'yicha 12 yangi e'lon", time:"10 daqiqa oldin" },
    { icon:'ph-trend-down', text:"Saqlangan e'lon narxi 3 000 $ tushdi — Novza, 2 xona", time:"2 soat oldin" },
    { icon:'ph-chat-circle-dots', text:"Golden House Agency chatda javob berdi", time:"kecha" }
  ];

  return { CITIES, DISTRICTS, DEAL_TYPES, PROP_TYPES, BANKS, DEVELOPERS, AGENTS, LISTINGS,
           SAVED_SEARCHES, DISTRICT_STATS, NOTIFICATIONS, RATE_UZS };
})();
