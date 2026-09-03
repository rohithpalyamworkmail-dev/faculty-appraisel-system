from global_schema import students,faculty,subjects,students_academic_details,alumni

department=["AI&DS","DS","CAI","CSE","ECE","EEE","MECH","CIVIL"]

semisters=list(range(1,9))

sections=["A","B","C","D","E"]

batches=["2023-2027","2024-2028","2025-2029","2026-2030"]

tables=[
    "students",
    "faculty",
    "subjects",
    "students_academic_details",
    "alumni",
    "faculty_images",
    "academic_results",
    "feedback",
    "hod_feedbacks",
    "project_guidence",
    "innovation_in_teaching",
    "obe_practice",
    "product_development_by_student",
    "seminar_workshop_conference_symposium_by_students",
    "competetion_contest__by_students",
    "language_certifications",
    "online_certifications",
    "internships_inplant_training",
    "special_awards",
    "student_involvements_in_startups",
    "competetive_examinations",
    "placements",
    "examination_results_faculty",
    "ict_skill_rack",
    "coding_data",
    "publications_conferences_journals_book_chapters",
    "patent_copy_rights",
    "consultancy_funding_grants",
    "citation_impacts",
    "phd_guidance",
    "book_publications",
    "on_campus_recruitments_by_faculty",
    "guest_lectures",
    "online_certifications_4weeks",
    "mooc_courses_by_faculty",
    "news_letters_and_magazines",
    "nirf_event_participations",
    "special_awards_fellowships",
    "faculty_exchanges",
    "extension_activities",
    "alumni_connection_by_faculties",
    "collaborations_industry_institute",
    "value_added_courses",
    "organizing_international_conference",
    "event_organizations",
    "membership"
]

india_states_districts={
    "Andhra Pradesh":[
        "Alluri Sitharama Raju","Anakapalli","Ananthapuramu","Annamayya",
        "Bapatla","Chittoor","Dr. B.R. Ambedkar Konaseema","East Godavari",
        "Eluru","Guntur","Kakinada","Krishna","Kurnool","Nandyal","NTR",
        "Palnadu","Parvathipuram Manyam","Prakasam","Srikakulam",
        "Sri Potti Sriramulu Nellore","Tirupati","Visakhapatnam",
        "Vizianagaram","West Godavari","YSR Kadapa","Markapuram","Polavaram"
    ],

    "Arunachal Pradesh":[
        "Anjaw","Bichom","Changlang","Dibang Valley","East Kameng","East Siang",
        "Itanagar Capital Complex","Kamle","Keyi Panyor","Kra Daadi",
        "Kurung Kumey","Lepa Rada","Lohit","Longding","Lower Dibang Valley",
        "Lower Siang","Lower Subansiri","Namsai","Pakke-Kessang","Papum Pare",
        "Shi Yomi","Siang","Tawang","Tirap","Upper Siang","Upper Subansiri",
        "West Kameng","West Siang"
    ],

    "Assam":[
        "Baksa","Bajali","Barpeta","Biswanath","Bongaigaon","Cachar",
        "Charaideo","Chirang","Darrang","Dhemaji","Dhubri","Dibrugarh",
        "Dima Hasao","Goalpara","Golaghat","Hailakandi","Hojai","Jorhat",
        "Kamrup","Kamrup Metropolitan","Karbi Anglong","Kokrajhar",
        "Lakhimpur","Majuli","Morigaon","Nagaon","Nalbari","Sivasagar",
        "Sonitpur","South Salmara-Mankachar","Tamulpur","Tinsukia",
        "Udalguri","West Karbi Anglong","Sribhumi"
    ],

    "Bihar":[
        "Araria","Arwal","Aurangabad","Banka","Begusarai","Bhagalpur",
        "Bhojpur","Buxar","Darbhanga","East Champaran","Gaya","Gopalganj",
        "Jamui","Jehanabad","Kaimur","Katihar","Khagaria","Kishanganj",
        "Lakhisarai","Madhepura","Madhubani","Munger","Muzaffarpur",
        "Nalanda","Nawada","Patna","Purnia","Rohtas","Saharsa","Samastipur",
        "Saran","Sheikhpura","Sheohar","Sitamarhi","Siwan","Supaul",
        "Vaishali","West Champaran"
    ],

    "Chhattisgarh":[
        "Balod","Baloda Bazar","Balrampur-Ramanujganj","Bastar","Bemetara",
        "Bijapur","Bilaspur","Dantewada","Dhamtari","Durg","Gariaband",
        "Gaurela-Pendra-Marwahi","Janjgir-Champa","Jashpur","Kabirdham",
        "Kanker","Khairagarh-Chhuikhadan-Gandai","Kondagaon","Korba","Korea",
        "Mahasamund","Manendragarh-Chirmiri-Bharatpur",
        "Mohla-Manpur-Ambagarh Chowki","Mungeli","Narayanpur","Raigarh",
        "Raipur","Rajnandgaon","Sakti","Sarangarh-Bilaigarh","Sukma",
        "Surajpur","Surguja"
    ],

    "Goa":[
        "North Goa","South Goa"
    ],

    "Gujarat":[
        "Ahmedabad","Amreli","Anand","Aravalli","Banaskantha","Bharuch",
        "Bhavnagar","Botad","Chhota Udaipur","Dahod","Dang","Devbhumi Dwarka",
        "Gandhinagar","Gir Somnath","Jamnagar","Junagadh","Kachchh","Kheda",
        "Mahisagar","Mehsana","Morbi","Narmada","Navsari","Panchmahal",
        "Patan","Porbandar","Rajkot","Sabarkantha","Surat","Surendranagar",
        "Tapi","Vadodara","Valsad"
    ],

    "Haryana":[
        "Ambala","Bhiwani","Charkhi Dadri","Faridabad","Fatehabad",
        "Gurugram","Hisar","Jhajjar","Jind","Kaithal","Karnal","Kurukshetra",
        "Mahendragarh","Nuh","Palwal","Panchkula","Panipat","Rewari",
        "Rohtak","Sirsa","Sonipat","Yamunanagar"
    ],

    "Himachal Pradesh":[
        "Bilaspur","Chamba","Hamirpur","Kangra","Kinnaur","Kullu",
        "Lahaul and Spiti","Mandi","Shimla","Sirmaur","Solan","Una"
    ],

    "Jharkhand":[
        "Bokaro","Chatra","Deoghar","Dhanbad","Dumka","East Singhbhum",
        "Garhwa","Giridih","Godda","Gumla","Hazaribagh","Jamtara","Khunti",
        "Koderma","Latehar","Lohardaga","Pakur","Palamu","Ramgarh","Ranchi",
        "Sahibganj","Seraikela Kharsawan","Simdega","West Singhbhum"
    ],

    "Karnataka":[
        "Bagalkote","Ballari","Belagavi","Bengaluru Rural","Bengaluru South",
        "Bengaluru Urban","Bidar","Chamarajanagar","Chikkaballapura",
        "Chikkamagaluru","Chitradurga","Dakshina Kannada","Davanagere",
        "Dharwad","Gadag","Hassan","Haveri","Kalaburagi","Kodagu","Kolar",
        "Koppal","Mandya","Mysuru","Raichur","Ramanagara","Shivamogga",
        "Tumakuru","Udupi","Uttara Kannada","Vijayapura","Yadgir"
    ],

    "Kerala":[
        "Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam",
        "Kottayam","Kozhikode","Malappuram","Palakkad","Pathanamthitta",
        "Thiruvananthapuram","Thrissur","Wayanad"
    ],

    "Madhya Pradesh":[
        "Agar-Malwa","Alirajpur","Anuppur","Ashoknagar","Balaghat","Barwani",
        "Betul","Bhind","Bhopal","Burhanpur","Chhatarpur","Chhindwara","Damoh",
        "Datia","Dewas","Dhar","Dindori","Guna","Gwalior","Harda","Indore",
        "Jabalpur","Jhabua","Katni","Khandwa","Khargone","Maihar","Mandla",
        "Mandsaur","Mauganj","Morena","Narmadapuram","Narsinghpur","Neemuch",
        "Niwari","Panna","Pandhurna","Raisen","Rajgarh","Ratlam","Rewa",
        "Sagar","Satna","Sehore","Seoni","Shahdol","Shajapur","Sheopur",
        "Shivpuri","Sidhi","Singrauli","Tikamgarh","Ujjain","Umaria","Vidisha"
    ],

    "Maharashtra":[
        "Ahilyanagar","Akola","Amravati","Beed","Bhandara","Buldhana",
        "Chandrapur","Chhatrapati Sambhajinagar","Dharashiv","Dhule",
        "Gadchiroli","Gondia","Hingoli","Jalgaon","Jalna","Kolhapur","Latur",
        "Mumbai","Mumbai Suburban","Nagpur","Nanded","Nandurbar","Nashik",
        "Palghar","Parbhani","Pune","Raigad","Ratnagiri","Sangli","Satara",
        "Sindhudurg","Solapur","Thane","Wardha","Washim","Yavatmal"
    ],

    "Manipur":[
        "Bishnupur","Chandel","Churachandpur","Imphal East","Imphal West",
        "Jiribam","Kakching","Kamjong","Kangpokpi","Noney","Pherzawl",
        "Senapati","Tamenglong","Tengnoupal","Thoubal","Ukhrul"
    ],

    "Meghalaya":[
        "East Garo Hills","East Jaintia Hills","East Khasi Hills",
        "Eastern West Khasi Hills","North Garo Hills","Ri Bhoi",
        "South Garo Hills","South West Garo Hills","South West Khasi Hills",
        "West Garo Hills","West Jaintia Hills","West Khasi Hills"
    ],

    "Mizoram":[
        "Aizawl","Champhai","Hnahthial","Khawzawl","Kolasib","Lawngtlai",
        "Lunglei","Mamit","Saiha","Saitual","Serchhip"
    ],

    "Nagaland":[
        "Chumoukedima","Dimapur","Kiphire","Kohima","Longleng","Meluri",
        "Mokokchung","Mon","Niuland","Noklak","Peren","Phek","Shamator",
        "Tseminyu","Tuensang","Wokha","Zunheboto"
    ],

    "Odisha":[
        "Angul","Boudh","Balangir","Bargarh","Balasore","Bhadrak","Cuttack",
        "Deogarh","Dhenkanal","Gajapati","Ganjam","Jagatsinghpur","Jajpur",
        "Jharsuguda","Kalahandi","Kandhamal","Kendrapara","Keonjhar","Khordha",
        "Koraput","Malkangiri","Mayurbhanj","Nabarangpur","Nayagarh","Nuapada",
        "Puri","Rayagada","Sambalpur","Subarnapur","Sundargarh"
    ],

    "Punjab":[
        "Amritsar","Barnala","Bathinda","Faridkot","Fatehgarh Sahib","Fazilka",
        "Ferozepur","Gurdaspur","Hoshiarpur","Jalandhar","Kapurthala",
        "Ludhiana","Malerkotla","Mansa","Moga","Pathankot","Patiala",
        "Rupnagar","Sahibzada Ajit Singh Nagar","Sangrur",
        "Shahid Bhagat Singh Nagar","Sri Muktsar Sahib","Tarn Taran"
    ],

    "Rajasthan":[
        "Ajmer","Alwar","Balotra","Banswara","Baran","Barmer","Beawar",
        "Bharatpur","Bhilwara","Bikaner","Bundi","Chittorgarh","Churu",
        "Dausa","Deeg","Dholpur","Didwana-Kuchaman","Dungarpur","Ganganagar",
        "Hanumangarh","Jaipur","Jaisalmer","Jalore","Jhalawar","Jhunjhunu",
        "Jodhpur","Karauli","Khairthal-Tijara","Kota","Kotputli-Behror",
        "Nagaur","Pali","Phalodi","Pratapgarh","Rajsamand","Salumbar",
        "Sawai Madhopur","Sikar","Sirohi","Tonk","Udaipur"
    ],

    "Sikkim":[
        "Gangtok","Gyalshing","Mangan","Namchi","Pakyong","Soreng"
    ],

    "Tamil Nadu":[
        "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore",
        "Dharmapuri","Dindigul","Erode","Kallakurichi","Kancheepuram",
        "Kanniyakumari","Karur","Krishnagiri","Madurai","Mayiladuthurai",
        "Nagapattinam","Namakkal","Perambalur","Pudukkottai","Ramanathapuram",
        "Ranipet","Salem","Sivaganga","Tenkasi","Thanjavur","The Nilgiris",
        "Theni","Thoothukudi","Tiruchirappalli","Tirunelveli","Tirupathur",
        "Tiruppur","Tiruvallur","Tiruvannamalai","Tiruvarur","Vellore",
        "Viluppuram","Virudhunagar"
    ],

    "Telangana":[
        "Adilabad","Bhadradri Kothagudem","Hanumakonda","Hyderabad",
        "Jagitial","Jangaon","Jayashankar Bhupalapally","Jogulamba Gadwal",
        "Kamareddy","Karimnagar","Khammam","Kumuram Bheem Asifabad",
        "Mahabubabad","Mahabubnagar","Mancherial","Medak",
        "Medchal-Malkajgiri","Mulugu","Nagarkurnool","Nalgonda","Narayanpet",
        "Nirmal","Nizamabad","Peddapalli","Rajanna Sircilla","Rangareddy",
        "Sangareddy","Siddipet","Suryapet","Vikarabad","Wanaparthy","Warangal",
        "Yadadri Bhuvanagiri"
    ],

    "Tripura":[
        "Dhalai","Gomati","Khowai","North Tripura","Sepahijala",
        "South Tripura","Unakoti","West Tripura"
    ],

    "Uttar Pradesh":[
        "Agra","Aligarh","Ambedkar Nagar","Amethi","Amroha","Auraiya",
        "Ayodhya","Azamgarh","Baghpat","Bahraich","Ballia","Balrampur",
        "Banda","Barabanki","Bareilly","Basti","Bhadohi","Bijnor","Budaun",
        "Bulandshahr","Chandauli","Chitrakoot","Deoria","Etah","Etawah",
        "Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar",
        "Ghaziabad","Ghazipur","Gonda","Gorakhpur","Hamirpur","Hapur",
        "Hardoi","Hathras","Jalaun","Jaunpur","Jhansi","Kannauj",
        "Kanpur Dehat","Kanpur Nagar","Kasganj","Kaushambi","Kheri","Kushinagar",
        "Lalitpur","Lucknow","Maharajganj","Mahoba","Mainpuri","Mathura","Mau",
        "Meerut","Mirzapur","Moradabad","Muzaffarnagar","Pilibhit",
        "Pratapgarh","Prayagraj","Raebareli","Rampur","Saharanpur","Sambhal",
        "Sant Kabir Nagar","Shahjahanpur","Shamli","Shravasti",
        "Siddharthnagar","Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi"
    ],

    "Uttarakhand":[
        "Almora","Bageshwar","Chamoli","Champawat","Dehradun","Haridwar",
        "Nainital","Pauri Garhwal","Pithoragarh","Rudraprayag","Tehri Garhwal",
        "Udham Singh Nagar","Uttarkashi"
    ],

    "West Bengal":[
        "Alipurduar","Bankura","Paschim Bardhaman","Purba Bardhaman","Birbhum",
        "Cooch Behar","Dakshin Dinajpur","Darjeeling","Hooghly","Howrah",
        "Jalpaiguri","Jhargram","Kalimpong","Kolkata","Maldah","Murshidabad",
        "Nadia","North 24 Parganas","South 24 Parganas","Uttar Dinajpur",
        "Paschim Medinipur","Purba Medinipur"
    ]
}

tables_list=["subjects","faculty","students","students_academic_details","alumni"]

tables_fields=[subjects,faculty,students,students_academic_details,alumni]