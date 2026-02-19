# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 22:14:28 2025

@author: mathaios
"""
import re
import time
import json
import hashlib
import requests
import pandas as pd
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode
from bs4 import BeautifulSoup

# ===================== INPUT =====================
# You can add multiple index pages if you have them (page 1, page 2, ...).
html_index_pages = [
    """<div id="main_content">

        <div class="single_title_space index_intro">
            <div class="archive_title">
                <a href="https://www.opengov.gr/home/" title="Αρχική"> Aρχική </a> &gt;  Διαβουλεύσεις      
            </div>
            
            <div class="archive_subpanel archivelist">
                <div class="single_subpanel_more_left">
                     <a href="https://www.opengov.gr:443/home/category/consultations/feed" target="_blank">Ροή RSS</a> <img src="https://www.opengov.gr/home/wp-content/themes/opengovhome/images/rss.png">
                                    </div>
                <div class="single_subpanel_more_right">

                                            <a href="https://www.opengov.gr/home/?cat=42">Διαβουλεύσεις »</a>
                                                                <a href="https://www.opengov.gr/home/?cat=24">Προσκλήσεις »</a>
                                                        </div>
            </div>
        </div>
        
        <div class="index_listing downspace_item archive_listing">        
            <div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 1 από 60</span><span class="current">1</span><a class="page larger" title="Σελίδα 2" href="https://www.opengov.gr/home/category/consultations/page/2">2</a><a class="page larger" title="Σελίδα 3" href="https://www.opengov.gr/home/category/consultations/page/3">3</a><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/2">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div>                        </div>
            <div class="downspace_item_content archive_list">
            <ul>
                                    <li>
                        <p><a href="https://www.opengov.gr/yyka/?p=5510">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας: «ΡΥΘΜΙΣΕΙΣ ΓΙΑ ΤΗΝ ΕΝΙΣΧΥΣΗ ΤΗΣ ΔΗΜΟΣΙΑΣ ΥΓΕΙΑΣ ΚΑΙ ΤΗΝ ΑΝΑΒΑΘΜΙΣΗ ΤΩΝ ΥΠΗΡΕΣΙΩΝ ΥΓΕΙΑΣ»</a></p>                        <span class="start">24 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/mindefence/?p=7284">Διαβούλευση για το Σχέδιο του Εθνικού Στρατιωτικού Κανονισμού Αξιοπλοΐας (ΕΣΚΑ) 147 «Οργανισμοί Εκπαίδευσης Συντήρησης Αεροσκαφών» της Εθνικής Στρατιωτικής Αρχής Αξιοπλοΐας (ΕΣΑΑ)</a></p>                        <span class="start">19 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/mindefence/?p=7274">Διαβούλευση για το Σχέδιο του Εθνικού Στρατιωτικού Κανονισμού Αξιοπλοΐας (ΕΣΚΑ) 66 «Αδειοδότηση Προσωπικού Συντήρησης Αεροσκαφών» της Εθνικής Στρατιωτικής Αρχής Αξιοπλοΐας (ΕΣΑΑ)</a></p>                        <span class="start">19 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ypep/?p=1040">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υφυπουργού στον Πρωθυπουργό με τίτλο: «Εκσυγχρονισμός νομικού πλαισίου οργάνωσης και λειτουργίας της «Ελληνικής Ραδιοφωνίας Τηλεόρασης Ανώνυμης Εταιρείας (Ε.Ρ.Τ. Α.Ε.)» και ενίσχυση του δημόσιου χαρακτήρα της και της ανταγωνιστικότητάς της στην αγορά των Μέσων Μαζικής Ενημέρωσης – Λήψη μέτρων για την εφαρμογή του Κανονισμού (ΕΕ) 2024/1083 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου, της 11ης Απριλίου 2024, σχετικά με τη θέσπιση κοινού πλαισίου για τις υπηρεσίες μέσων ενημέρωσης στην εσωτερική αγορά και την τροποποίηση της οδηγίας 2010/13/ΕΕ (Ευρωπαϊκός Κανονισμός για την ελευθερία των μέσων ενημέρωσης – EUROPEAN MEDIA FREEDOM ACT)»</a></p>                        <span class="start">17 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ypepth/?p=6927">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Παιδείας, Θρησκευμάτων και Αθλητισμού με τίτλο «Σύσταση Ακαδημιών Επαγγελματικής Κατάρτισης – Ένταξη των Ακαδημιών στο Εθνικό Σύστημα Επαγγελματικής Εκπαίδευσης και άλλα θέματα επαγγελματικής κατάρτισης»</a></p>                        <span class="start">11 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/yptp/?p=3390">Δημόσια ηλεκτρονική διαβούλευση για το Σχέδιο Νόμου: «Προσδιορισμός κρίσιμων οντοτήτων, ορισμός της Γενικής Γραμματείας Προστασίας Κρίσιμων Οντοτήτων του Υπουργείου Προστασίας του Πολίτης ως αρμόδιας αρχής και ενιαίου σημείου επαφής – Εποπτεία συμμόρφωσης, επιβολή μέτρων και κυρώσεων -Ενσωμάτωση της Οδηγίας (ΕΕ) 2022/2557 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου, της 14ης Δεκεμβρίου 2022, για την ανθεκτικότητα των κρίσιμων οντοτήτων και την κατάργηση της Οδηγίας 2008/114/ΕΚ του Συμβουλίου»</a></p>                        <span class="start">4 Σεπτέμβριος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/minfin/?p=13498">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών με τίτλο: «Ενίσχυση των υπηρεσιών των Αναπτυξιακών Προγραμμάτων και συναφή οργανωτικά και διοικητικά ζητήματα»</a></p>                        <span class="start">28 Αύγουστος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/minlab/?p=6252">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εργασίας και Κοινωνικής Ασφάλισης με τίτλο «Δίκαιη Εργασία για Όλους: Απλοποίηση της Νομοθεσίας – Στήριξη στον Εργαζόμενο – Προστασία στην Πράξη»</a></p>                        <span class="start">25 Αύγουστος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ministryofjustice/?p=17977" target="_blank" rel="noopener">Καθορισμός αδικημάτων και κυρώσεων σε βάρος φυσικών και νομικών προσώπων για παραβίαση των περιοριστικών μέτρων της Ευρωπαϊκής Ένωσης, ενσωμάτωση οδηγίας (ΕE) 2024/1226 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου της 24ης Απριλίου 2024 σχετικά με τον ορισμό των ποινικών αδικημάτων και των κυρώσεων για την παραβίαση των περιοριστικών μέτρων της Ένωσης και την τροποποίηση της οδηγίας (ΕΕ) 2018/1673 και λοιπές διατάξεις</a></p>                        <span class="start">8 Αύγουστος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/minfin/?p=13453">Έναρξη διαβούλευσης σχεδίου υπουργικής απόφασης «4η Αναθεώρηση Εθνικού Προγράμματος Ανάπτυξης (ΕΠΑ) 2021-2025»</a></p>                        <span class="start">4 Αύγουστος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/koinsynoik/?p=9652">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Κοινωνικής Συνοχής και Οικογένειας: «ΚΟΙΝΩΝΙΚΗ ΑΝΤΙΠΑΡΟΧΗ, ΚΟΙΝΩΝΙΚΗ ΜΙΣΘΩΣΗ, ΤΡΙΤΕΚΝΙΚΗ ΙΔΙΟΤΗΤΑ ΚΑΙ ΑΛΛΕΣ ΔΙΑΤΑΞΕΙΣ ΑΡΜΟΔΙΟΤΗΤΑΣ ΤΟΥ ΥΠΟΥΡΓΕΙΟΥ ΚΟΙΝΩΝΙΚΗΣ ΣΥΝΟΧΗΣ ΚΑΙ ΟΙΚΟΓΕΝΕΙΑΣ»</a></p>                        <span class="start">30 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/mindefence/?p=7252">Διαβούλευση για το Σχέδιο του Εθνικού Στρατιωτικού Κανονισμού Αξιοπλοΐας (ΕΣΚΑ) 21 «Πιστοποίηση Στρατιωτικών Αεροσκαφών και Συναφών Προϊόντων, Εξαρτημάτων και Συσκευών και Οργανισμών Σχεδίασης και Παραγωγής» της Εθνικής Στρατιωτικής Αρχής Αξιοπλοΐας (ΕΣΑΑ)</a></p>                        <span class="start">25 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/immigration/?p=1873">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Μετανάστευσης και Ασύλου με τίτλο: «Αναμόρφωση πλαισίου και διαδικασιών επιστροφών πολιτών τρίτων χωρών – Λοιπές ρυθμίσεις του Υπουργείου Μετανάστευσης και Ασύλου»</a></p>                        <span class="start">17 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ypepth/?p=6843">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Παιδείας, Θρησκευμάτων και Αθλητισμού με τίτλο: «Σύσταση νομικού προσώπου δημοσίου δικαίου με την επωνυμία «Ελληνορθόδοξη Ιερά Βασιλική Αυτόνομη Μονή του Αγίου και Θεοβάδιστου όρους Σινά στην Ελλάδα», ρυθμίσεις θεμάτων αρμοδιότητας Γενικής Γραμματείας Θρησκευμάτων, ενίσχυση της ασφάλειας στα ανώτατα εκπαιδευτικά ιδρύματα, διατάξεις για τον αθλητισμό και λοιπές ρυθμίσεις»</a></p>                        <span class="start">9 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ypes/?p=9485">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εσωτερικών με τίτλο:Αναμόρφωση του πειθαρχικού δικαίου των υπαλλήλων του δημόσιου τομέα, σύσταση Ελληνικού Κέντρου Εμπειρογνωμοσύνης Διοικητικών Μεταρρυθμίσεων και λοιπές διατάξεις</a></p>                        <span class="start">7 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/consultations/?p=3989">Δημόσια ηλεκτρονική διαβούλευση του Αντιπροέδρου της Κυβέρνησης για το εθνικό Κοινωνικό Κλιματικό Σχέδιο</a></p>                        <span class="start">4 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/mindefence/?p=7191">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Άμυνας με τίτλο: «Αξιοποίηση ακίνητης περιουσίας Ενόπλων Δυνάμεων – Σύσταση Ταμείου Ακινήτων Εθνικής Άμυνας και Φορέα Αξιοποίησης Ακινήτων Ενόπλων Δυνάμεων – Σχέδιο δράσεων για τη διαχείριση των στεγαστικών αναγκών των στελεχών των Ενόπλων Δυνάμεων»</a></p>                        <span class="start">4 Ιούλιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/ministryofjustice/?p=17906">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Δικαιοσύνης με τίτλο «Παρεμβάσεις στον Κώδικα Πολιτικής Δικονομίας – Τροποποιήσεις σχετικά με τη δημοσίευση διαθηκών – Τροποποιήσεις στο ρυθμιστικό πλαίσιο των ανακοπών κατά της αναγκαστικής εκτέλεσης με σκοπό την επιτάχυνση της εκδίκασης – Λοιπές διατάξεις αρμοδιότητας του Υπουργείου Δικαιοσύνης»</a></p>                        <span class="start">27 Ιούνιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/minfin/?p=13407">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών με τίτλο: «ΕΘΝΙΚΟΣ ΤΕΛΩΝΕΙΑΚΟΣ ΚΩΔΙΚΑΣ ΚΑΙ ΑΛΛΕΣ ΔΙΑΤΑΞΕΙΣ – ΣΥΝΤΑΞΙΟΔΟΤΙΚΕΣ ΔΙΑΤΑΞΕΙΣ»</a></p>                        <span class="start">24 Ιούνιος, 2025</span>
                    </li>
                                    <li>
                        <p><a href="https://www.opengov.gr/yme/?p=5532">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υποδομών και Μεταφορών με τον τίτλο: «Αναβάθμιση της ασφάλειας των σιδηροδρόμων, οργανωτική ενίσχυση της Ρυθμιστικής Αρχής Σιδηροδρόμων, του Εθνικού Οργανισμού Διερεύνησης Αεροπορικών και Σιδηροδρομικών Ατυχημάτων και Ασφάλειας Μεταφορών και της εταιρείας Σιδηρόδρομοι Ελλάδος Μονοπρόσωπη Α.Ε. και λοιπές διατάξεις»</a></p>                        <span class="start">12 Ιούνιος, 2025</span>
                    </li>
                            </ul>
            </div>
            <div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 1 από 60</span><span class="current">1</span><a class="page larger" title="Σελίδα 2" href="https://www.opengov.gr/home/category/consultations/page/2">2</a><a class="page larger" title="Σελίδα 3" href="https://www.opengov.gr/home/category/consultations/page/3">3</a><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/2">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div></div>
        </div>
    </div>""",
    """ <div id="main_content">

		<div class="single_title_space index_intro">
			<div class="archive_title">
				<a href="https://www.opengov.gr/home/" title="Αρχική"> Aρχική </a> &gt;	Διαβουλεύσεις      
    		</div>
			
			<div class="archive_subpanel archivelist">
				<div class="single_subpanel_more_left">
					 <a href="https://www.opengov.gr:443/home/category/consultations/page/2/feed" target="_blank">Ροή RSS</a> <img src="https://www.opengov.gr/home/wp-content/themes/opengovhome/images/rss.png">
									</div>
				<div class="single_subpanel_more_right">

											<a href="https://www.opengov.gr/home/?cat=42">Διαβουλεύσεις »</a>
																<a href="https://www.opengov.gr/home/?cat=24">Προσκλήσεις »</a>
														</div>
			</div>
		</div>
		
		<div class="index_listing downspace_item archive_listing">		
			<div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 2 από 60</span><a class="previouspostslink" rel="prev" href="https://www.opengov.gr/home/category/consultations/">«</a><a class="page smaller" title="Σελίδα 1" href="https://www.opengov.gr/home/category/consultations/">1</a><span class="current">2</span><a class="page larger" title="Σελίδα 3" href="https://www.opengov.gr/home/category/consultations/page/3">3</a><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/3">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div>						</div>
			<div class="downspace_item_content archive_list">
			<ul>
									<li>
						<p><a href="https://www.opengov.gr/yme/?p=5532">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υποδομών και Μεταφορών με τον τίτλο: «Αναβάθμιση της ασφάλειας των σιδηροδρόμων, οργανωτική ενίσχυση της Ρυθμιστικής Αρχής Σιδηροδρόμων, του Εθνικού Οργανισμού Διερεύνησης Αεροπορικών και Σιδηροδρομικών Ατυχημάτων και Ασφάλειας Μεταφορών και της εταιρείας Σιδηρόδρομοι Ελλάδος Μονοπρόσωπη Α.Ε. και λοιπές διατάξεις»</a></p>						<span class="start">12 Ιούνιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/minfin/?p=13357">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών με τίτλο: «Διασφάλιση δημοσιονομικής ισορροπίας: Μεταρρύθμιση πλαισίου δημοσιονομικής διαχείρισης – Τροποποίηση ν. 4270/2014 για την ενσωμάτωση της Οδηγίας (ΕΕ) 2024/1265 του Συμβουλίου της 29ης Απριλίου 2024 για την τροποποίηση της Οδηγίας 2011/85/ΕΕ σχετικά με τις απαιτήσεις για τα δημοσιονομικά πλαίσια των κρατών μελών και λοιπές διατάξεις»</a></p>						<span class="start">5 Ιούνιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/minenv/?p=13717">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου: «ΠΛΑΙΣΙΟ ΓΙΑ ΤΗΝ ΠΡΟΩΘΗΣΗ ΤΗΣ ΠΑΡΑΓΩΓΗΣ ΒΙΟΜΕΘΑΝΙΟΥ, ΚΑΝΟΝΕΣ ΓΙΑ ΤΗΝ ΟΡΓΑΝΩΣΗ ΤΗΣ ΑΓΟΡΑΣ ΠΑΡΑΓΩΓΗΣ ΥΔΡΟΓΟΝΟΥ ΚΑΙ ΤΑ ΓΕΩΓΡΑΦΙΚΑ ΠΕΡΙΟΡΙΣΜΕΝΑ ΔΙΚΤΥΑ ΥΔΡΟΓΟΝΟΥ – ΜΕΡΙΚΗ ΕΝΣΩΜΑΤΩΣΗ ΟΔΗΓΙΑΣ (ΕΕ) 2024/1788 ΚΑΙ ΑΛΛΕΣ ΔΙΑΤΑΞΕΙΣ ΓΙΑ ΤΗΝ ΠΡΟΣΤΑΣΙΑ ΤΟΥ ΠΕΡΙΒΑΛΛΟΝΤΟΣ»</a></p>						<span class="start">2 Ιούνιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/yyka/?p=5399">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας «Προστασία των ανηλίκων από προϊόντα καπνού και αλκοόλ – Ρυθμίσεις για μη καπνικά προϊόντα – Ψηφιακό μητρώο ελέγχου προϊόντων καπνού, αλκοόλ και λοιπών μη καπνικών προϊόντων και άλλες διατάξεις»</a></p>						<span class="start">31 Μάιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypoian/?p=14356">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ανάπτυξης με τίτλο «Αναμόρφωση του πλαισίου για την επαγγελματική κατάρτιση υπαλλήλων που χειρίζονται δημόσιες συμβάσεις, του πλαισίου για την προετοιμασία και την ανάθεση δημοσίων συμβάσεων και την έννομη προστασία στον τομέα των δημοσίων συμβάσεων, του πλαισίου εθνικών υποδομών ποιότητας και του πλαισίου ίδρυσης, επέκτασης και εκσυγχρονισμού των μεταποιητικών δραστηριοτήτων στην Περιφέρεια Αττικής»</a></p>						<span class="start">29 Μάιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/civilprotection/?p=7473">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Κλιματικής Κρίσης και Πολιτικής Προστασίας με τον τίτλο: «Πλαίσιο για την ενίσχυση της ανθεκτικότητας: Διατάξεις για την πολιτική προστασία και το Πυροσβεστικό Σώμα»</a></p>						<span class="start">23 Μάιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypep/?p=934">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υφυπουργού στον Πρωθυπουργό με τίτλο: «Ενίσχυση της δημοσιότητας και της διαφάνειας στον έντυπο και ηλεκτρονικό τύπο –Τροποποιήσεις ν. 5005/2022 και ν. 3548/2007 και λοιπές διατάξεις»</a></p>						<span class="start">3 Μάιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypoian/?p=14231">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ανάπτυξης με τον τίτλο: «Βιώσιμη ανάπτυξη, παραγωγικός μετασχηματισμός της ελληνικής οικονομίας – Τροποποίηση διατάξεων του αναπτυξιακού νόμου 4887/2022 Αναπτυξιακός Νόμος – Ελλάδα Ισχυρή Ανάπτυξη – και λοιπές διατάξεις»</a></p>						<span class="start">18 Απρίλιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ministryofjustice/?p=17805">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Δικαιοσύνης με τίτλο: «Παρεμβάσεις στο νομοθετικό πλαίσιο της Εθνικής Σχολής Δικαστικών Λειτουργών, στον Κώδικα Οργανισμού Δικαστηρίων και Κατάστασης Δικαστικών Λειτουργών και στον Κώδικα Συμβολαιογράφων και λοιπές διατάξεις του Υπουργείου Δικαιοσύνης»</a></p>						<span class="start">13 Απρίλιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypex/?p=1155">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εξωτερικών με τίτλο: «Λήψη μέτρων εφαρμογής του Κανονισμού (ΕΕ) 2019/452 για τη θέσπιση πλαισίου ελέγχου άμεσων ξένων επενδύσεων στην Ένωση για λόγους ασφάλειας ή δημόσιας τάξης»</a></p>						<span class="start">3 Απρίλιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/yyka/?p=5278">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας με τίτλο: «Σύσταση και οργάνωση νομικού προσώπου δημοσίου δικαίου με την επωνυμία «Σύλλογος Διαιτολόγων – Διατροφολόγων Ελλάδος» και άλλες διατάξεις αρμοδιότητας Υπουργείου Υγείας»</a></p>						<span class="start">27 Μάρτιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/mindefence/?p=7117">Δημόσια ηλεκτρονική διαβούλευση για τη νομοθετική πρωτοβουλία του Υπουργείου Εθνικής Άμυνας, υπό τον τίτλο: «Ρύθμιση υγειονομικών θεμάτων των Ενόπλων Δυνάμεων και λοιπές διατάξεις»</a></p>						<span class="start">18 Μάρτιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/minfin/?p=13270">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών με τίτλο: «Ενίσχυση της κεφαλαιαγοράς»</a></p>						<span class="start">3 Μάρτιος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/digitalandbrief/?p=3480">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ψηφιακής Διακυβέρνησης με τίτλο: «Μέτρα εφαρμογής του Κανονισμού (ΕΕ) 2022/868 (πράξη για τη διακυβέρνηση δεδομένων)- Ορισμός αρμόδιας αρχής για την εφαρμογή του Κανονισμού (ΕΕ) 2024/903 (Κανονισμός για τη διαλειτουργική Ευρώπη)-Ηλεκτρονική εφαρμογή “my street” και λοιπές ρυθμίσεις προώθησης του ψηφιακού μετασχηματισμού».</a></p>						<span class="start">15 Φεβρουάριος, 2025</span>
					</li>
									<li>
						<p><a href="http://opengov.gr/minenv/?p=13560">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Περιβάλλοντος και Ενέργειας με τίτλο: «ΕΚΣΥΓΧΡΟΝΙΣΜΟΣ ΤΟΥ ΠΛΑΙΣΙΟΥ ΤΩΝ ΥΠΗΡΕΣΙΩΝ ΥΔΡΕΥΣΗΣ ΚΑΙ ΑΠΟΧΕΤΕΥΣΗΣ ΚΑΙ ΕΠΕΙΓΟΥΣΕΣ ΕΝΕΡΓΕΙΑΚΕΣ ΚΑΙ ΠΟΛΕΟΔΟΜΙΚΕΣ ΡΥΘΜΙΣΕΙΣ».</a></p>						<span class="start">14 Φεβρουάριος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/yptp/?p=3330">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Προστασίας του Πολίτη, με τίτλο: «Αναδιοργάνωση της δομής της Ελληνικής Αστυνομίας και αναβάθμιση της εκπαίδευσης του ένστολου προσωπικού της – Εκσυγχρονισμός του θεσμού της ηλεκτρονικής επιτήρησης υπόδικων, κατάδικων και κρατούμενων σε άδεια – Ρύθμιση θεμάτων κρατούμενων σε σωφρονιστικά καταστήματα και άλλων θεμάτων αρμοδιότητας του Υπουργείου Προστασίας του Πολίτη».</a></p>						<span class="start">8 Φεβρουάριος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypaat/?p=3279">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Αγροτικής Ανάπτυξης και Τροφίμων με τίτλο: «Ρυθμίσεις για τις διεπαγγελματικές οργανώσεις, την ενίσχυση του αγροτικού τομέα, την οργάνωση των υπηρεσιών και εποπτευόμενων φορέων του Υπουργείου Αγροτικής Ανάπτυξης και Τροφίμων και την επανεκκίνηση της αγροτικής οικονομίας»</a></p>						<span class="start">24 Ιανουάριος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/cultureathl/?p=9313">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Πολιτισμού με τίτλο «Αναδιοργάνωση του νομικού προσώπου δημοσίου δικαίου με την επωνυμία «Εθνική Πινακοθήκη-Μουσείου Αλεξάνδρου Σούτσου» και του νομικού προσώπου ιδιωτικού δικαίου με την επωνυμία «Μητροπολιτικός Οργανισμός Μουσείων Εικαστικών Τεχνών Θεσσαλονίκης», ενίσχυση των δράσεων του Οργανισμού Μεγάρου Μουσικής Θεσσαλονίκης και του Φεστιβάλ Κινηματογράφου Θεσσαλονίκης, μετονομασία του Προπαρασκευαστικού και Επαγγελματικού Σχολείου καλών Τεχνών Πανόρμου Τήνου σε Ανώτερη Σχολή Μαρμαροτεχνίας Τήνου και αναμόρφωση του πλαισίου λειτουργίας της, ρυθμίσεις για το πρόγραμμα στήριξης οπτικοακουστικών έργων στην Ελλάδα και λοιπές διατάξεις αρμοδιότητας του Υπουργείου Πολιτισμού»</a></p>						<span class="start">18 Ιανουάριος, 2025</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/koinsynoik/?p=9557">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Κοινωνικής Συνοχής και Οικογένειας: «Μέτρα για την ισόρροπη εκπροσώπηση των φύλων σε θέσεις διευθυντικών στελεχών των εισηγμένων εταιρειών, των μη εισηγμένων ανωνύμων εταιρειών και των δημοσίων επιχειρήσεων – Ενσωμάτωση της Οδηγίας (Ε.Ε.) 2022/2381 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου της 23ης Νοεμβρίου 2022»</a></p>						<span class="start">16 Ιανουάριος, 2025</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/yme/?p=5447">Δημόσια διαβούλευση για το σχέδιο νόμου του Υπουργείου Υποδομών και Μεταφορών με τίτλο: «ΝΕΟ ΚΥΡΩΤΙΚΟ ΠΛΑΙΣΙΟ ΤΟΥ ΚΩΔΙΚΑ ΟΔΙΚΗΣ ΚΥΚΛΟΦΟΡΙΑΣ ΚΑΙ ΛΟΙΠΕΣ ΔΙΑΤΑΞΕΙΣ ΓΙΑ ΤΗΝ ΑΣΦΑΛΗ ΚΙΝΗΤΙΚΟΤΗΤΑ»</a></p>						<span class="start">4 Ιανουάριος, 2025</span>
					</li>
							</ul>
			</div>
			<div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 2 από 60</span><a class="previouspostslink" rel="prev" href="https://www.opengov.gr/home/category/consultations/">«</a><a class="page smaller" title="Σελίδα 1" href="https://www.opengov.gr/home/category/consultations/">1</a><span class="current">2</span><a class="page larger" title="Σελίδα 3" href="https://www.opengov.gr/home/category/consultations/page/3">3</a><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/3">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div></div>
		</div>
	</div> """,
    """ <div id="main_content">

		<div class="single_title_space index_intro">
			<div class="archive_title">
				<a href="https://www.opengov.gr/home/" title="Αρχική"> Aρχική </a> &gt;	Διαβουλεύσεις      
    		</div>
			
			<div class="archive_subpanel archivelist">
				<div class="single_subpanel_more_left">
					 <a href="https://www.opengov.gr:443/home/category/consultations/page/3/feed" target="_blank">Ροή RSS</a> <img src="https://www.opengov.gr/home/wp-content/themes/opengovhome/images/rss.png">
									</div>
				<div class="single_subpanel_more_right">

											<a href="https://www.opengov.gr/home/?cat=42">Διαβουλεύσεις »</a>
																<a href="https://www.opengov.gr/home/?cat=24">Προσκλήσεις »</a>
														</div>
			</div>
		</div>
		
		<div class="index_listing downspace_item archive_listing">		
			<div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 3 από 60</span><a class="previouspostslink" rel="prev" href="https://www.opengov.gr/home/category/consultations/page/2">«</a><a class="page smaller" title="Σελίδα 1" href="https://www.opengov.gr/home/category/consultations/">1</a><a class="page smaller" title="Σελίδα 2" href="https://www.opengov.gr/home/category/consultations/page/2">2</a><span class="current">3</span><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/4">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div>						</div>
			<div class="downspace_item_content archive_list">
			<ul>
									<li>
						<p><a href="https://www.opengov.gr/yyka/?p=5202">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας με τον τίτλο: «Αναμόρφωση του Εθνικού Συστήματος Τραύματος»</a></p>						<span class="start">28 Δεκέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ypepth/?p=6782">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Παιδείας, Θρησκευμάτων και Αθλητισμού με τίτλο: «Ρυθμίσεις για την ενίσχυση του ερασιτεχνικού και του επαγγελματικού αθλητισμού»</a></p>						<span class="start">26 Δεκέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="https://www.opengov.gr/ministryofjustice/?p=17711">Δημόσια ηλεκτρονική διαβούλευση του Υπουργείου Δικαιοσύνης με τίτλο «Αντιμετώπιση νέων μορφών βίας κατά των γυναικών –Ενσωμάτωση της Οδηγίας (ΕΕ) 2024/1385 – Πρόσθετες ρυθμίσεις στον νόμο περί ενδοοικογενειακής βίας –Αναδιοργάνωση των ιατροδικαστικών υπηρεσιών –Ενίσχυση της λειτουργίας της Eurojust- Μέτρα για την προστασία των ανηλίκων και την καταπολέμηση της εγκληματικότητας στον Ποινικό Κώδικα και τον Κώδικα Ποινικής Δικονομίας – Δικονομικές διατάξεις αρμοδιότητας των τακτικών διοικητικών δικαστηρίων και άλλες ρυθμίσεις»</a></p>						<span class="start">26 Δεκέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/tourism/?p=2336">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Τουρισμού με τίτλο: «Θέσπιση προδιαγραφών ακινήτων βραχυχρόνιας μίσθωσης, περιβαλλοντική κατάταξη καταλυμάτων, απλούστευση διαδικασίας ίδρυσης τουριστικών επιχειρήσεων και ειδικότερες διατάξεις ελέγχου και ενίσχυσης πλαισίου τουριστικών υποδομών»</a></p>						<span class="start">5 Δεκέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/yme/?p=5397">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υποδομών και Μεταφορών με τίτλο: «Αναδιάρθρωση σιδηροδρομικού τομέα και ενίσχυση ρυθμιστικών φορέων μεταφορών»</a></p>						<span class="start">27 Νοέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/ypex/?p=1045">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εξωτερικών: «ΠΑΡΕΜΒΑΣΕΙΣ ΣΤΗΝ ΟΡΓΑΝΩΣΗ ΚΑΙ ΤΗ ΛΕΙΤΟΥΡΓΙΑ ΤΟΥ ΥΠΟΥΡΓΕΙΟΥ ΕΞΩΤΕΡΙΚΩΝ»</a></p>						<span class="start">20 Νοέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/ypoian/?p=14116">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ανάπτυξης με τίτλο: «Ενσωμάτωση της Οδηγίας (ΕΕ) 2022/2464 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου, της 14ης Δεκεμβρίου 2022, για την τροποποίηση του Κανονισμού (ΕΕ) 537/2014, της Οδηγίας 2004/109/ΕΚ, της Οδηγίας 2006/ 43/ΕΚ και της Οδηγίας 2013/34/ΕΕ, όσον αφορά την υποβολή εκθέσεων βιωσιμότητας από τις εταιρείες (L 322) και της κατ’ εξουσιοδότηση Οδηγίας (ΕΕ) 2023/2775 της Επιτροπής, της 17ης Οκτωβρίου 2023, για την τροποποίηση της Οδηγίας 2013/34/ΕΕ του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου όσον αφορά τις προσαρμογές των κριτηρίων μεγέθους για τις πολύ μικρές, τις μικρές, τις μεσαίες και τις μεγάλες επιχειρήσεις ή ομίλους»</a></p>						<span class="start">15 Νοέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minlab/?p=6179">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εργασίας και Κοινωνικής Ασφάλισης με τίτλο «Ενσωμάτωση της Οδηγίας (Ε.Ε.) 2022/2041 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου της 19ης Οκτωβρίου 2022 για επαρκείς κατώτατους μισθούς στην Ευρωπαϊκή Ένωση – Αναπροσαρμογή μισθών προσωπικού δημοσίου τομέα – Ρυθμίσεις για τον καθορισμό κατώτατου μισθού για τα έτη 2025, 2026 και 2027»</a></p>						<span class="start">7 Νοέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minfin/?p=13184">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών: «Μέτρα για την ενίσχυση του εισοδήματος, φορολογικά κίνητρα για την καινοτομία και τους μετασχηματισμούς επιχειρήσεων και άλλες διατάξεις»</a></p>						<span class="start">6 Νοέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/yyka/?p=5124">Δημόσια διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας: «Ρυθμίσεις για την ενίσχυση του Εθνικού Συστήματος Υγείας και την παρακολούθηση και αξιολόγηση της φαρμακευτικής δαπάνης»</a></p>						<span class="start">25 Οκτώβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/digitalandbrief/?p=3398">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ψηφιακής Διακυβέρνησης με τίτλο: «Ενσωμάτωση της Οδηγίας (ΕΕ) 2022/2555 του Ευρωπαϊκού Κοινοβουλίου και του Συμβουλίου, της 14ης Δεκεμβρίου 2022, σχετικά με μέτρα για υψηλό κοινό επίπεδο κυβερνοασφάλειας σε ολόκληρη την Ένωση, την τροποποίηση του Κανονισμού (ΕΕ) 910/2014 και της Οδηγίας (ΕΕ) 2018/1972, και την κατάργηση της Οδηγίας (ΕΕ) 2016/1148 (Οδηγία NIS 2) και άλλες διατάξεις».</a></p>						<span class="start">19 Οκτώβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/yyka/?p=5021">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Υγείας με τίτλο: «Αναμόρφωση του θεσμού του Προσωπικού Ιατρού – Σύσταση Πανεπιστημιακών Κέντρων Υγείας και άλλες διατάξεις του Υπουργείου Υγείας»</a></p>						<span class="start">24 Σεπτέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/ypes/?p=9210">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εσωτερικών με τίτλο: «Επιτάχυνση προσλήψεων μέσω Α.Σ.Ε.Π., σύστημα κινήτρων και ανταμοιβής δημοσίων υπαλλήλων και λοιπές διατάξεις για τη βελτίωση της λειτουργίας της δημόσιας διοίκησης»</a></p>						<span class="start">3 Σεπτέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/ypes/?p=9312">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εσωτερικών με τίτλο: «Ρυθμίσεις για τους χερσαίους συνοριακούς σταθμούς, την ενίσχυση των Οργανισμών Τοπικής Αυτοδιοίκησης και λοιπές διατάξεις»</a></p>						<span class="start">3 Σεπτέμβριος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minfin/?p=13118">Έναρξη Διαβούλευσης σχεδίου Υπουργικής Απόφασης «3η Αναθεώρηση Εθνικού Προγράμματος Ανάπτυξης (ΕΠΑ) 2021-2025»</a></p>						<span class="start">31 Αύγουστος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minenv/?p=13404">Δημόσια διαβούλευση για το σχέδιο νόμου «Ρυθμίσεις για τον εκσυγχρονισμό της διαχείρισης αποβλήτων, τη βελτίωση του πλαισίου εξοικονόμησης ενέργειας, την ανάπτυξη των έργων ενέργειας και την αντιμετώπιση πολεοδομικών ζητημάτων»</a></p>						<span class="start">30 Αύγουστος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/digitalandbrief/?p=3306">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Ψηφιακής Διακυβέρνησης με τίτλο: «Ολοκλήρωση της κτηματογράφησης, απλοποίηση διαδικασιών, χρήση τεχνητής νοημοσύνης και διατάξεις για τη λειτουργία του ν.π.δ.δ. «Ελληνικό Κτηματολόγιο», λοιπές διατάξεις του Υπουργείου Ψηφιακής Διακυβέρνησης»</a></p>						<span class="start">25 Αύγουστος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minenv/?p=13352">Δημόσια ηλεκτρονική διαβούλευση για το αναθεωρημένο Εθνικό Σχέδιο για την Ενέργεια και το Κλίμα (ΕΣΕΚ)</a></p>						<span class="start">22 Αύγουστος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/minfin/?p=13025">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Εθνικής Οικονομίας και Οικονομικών με τίτλο: «ΝΕΟ ΑΝΑΠΤΥΞΙΑΚΟ ΠΡΟΓΡΑΜΜΑ ΔΗΜΟΣΙΩΝ ΕΠΕΝΔΥΣΕΩΝ ΚΑΙ ΣΥΜΠΛΗΡΩΜΑΤΙΚΕΣ ΔΙΑΤΑΞΕΙΣ»</a></p>						<span class="start">16 Αύγουστος, 2024</span>
					</li>
									<li>
						<p><a href="http://www.opengov.gr/ministryofjustice/?p=17665">Δημόσια ηλεκτρονική διαβούλευση για το σχέδιο νόμου του Υπουργείου Δικαιοσύνης με τίτλο «ΠΑΡΕΜΒΑΣΕΙΣ ΣΤΟΝ ΚΩΔΙΚΑ ΠΟΛΙΤΙΚΗΣ ΔΙΚΟΝΟΜΙΑΣ, ΣΤΟΝ ΚΩΔΙΚΑ ΟΡΓΑΝΙΣΜΟΥ ΔΙΚΑΣΤΗΡΙΩΝ ΚΑΙ ΚΑΤΑΣΤΑΣΗΣ ΔΙΚΑΣΤΙΚΩΝ ΛΕΙΤΟΥΡΓΩΝ ΚΑΙ ΣΤΟΝ ΚΩΔΙΚΑ ΠΟΙΝΙΚΗΣ ΔΙΚΟΝΟΜΙΑΣ ΣΕ ΕΝΑΡΜΟΝΙΣΗ ΜΕ ΤΗΝ ΕΝΟΠΟΙΗΣΗ ΤΟΥ ΠΡΩΤΟΥ ΒΑΘΜΟΥ ΔΙΚΑΙΟΔΟΣΙΑΣ ΜΕ ΤΟΝ Ν. 5108/2024 – ΔΙΑΤΑΞΕΙΣ ΓΙΑ ΤΗ ΔΙΚΑΣΤΙΚΗ ΑΣΤΥΝΟΜΙΑ»</a></p>						<span class="start">16 Αύγουστος, 2024</span>
					</li>
							</ul>
			</div>
			<div class="downspace_item_title"><div class="wp-pagenavi">
<span class="pages">Σελίδα 3 από 60</span><a class="previouspostslink" rel="prev" href="https://www.opengov.gr/home/category/consultations/page/2">«</a><a class="page smaller" title="Σελίδα 1" href="https://www.opengov.gr/home/category/consultations/">1</a><a class="page smaller" title="Σελίδα 2" href="https://www.opengov.gr/home/category/consultations/page/2">2</a><span class="current">3</span><a class="page larger" title="Σελίδα 4" href="https://www.opengov.gr/home/category/consultations/page/4">4</a><a class="page larger" title="Σελίδα 5" href="https://www.opengov.gr/home/category/consultations/page/5">5</a><span class="extend">...</span><a class="larger page" title="Σελίδα 10" href="https://www.opengov.gr/home/category/consultations/page/10">10</a><a class="larger page" title="Σελίδα 20" href="https://www.opengov.gr/home/category/consultations/page/20">20</a><a class="larger page" title="Σελίδα 30" href="https://www.opengov.gr/home/category/consultations/page/30">30</a><span class="extend">...</span><a class="nextpostslink" rel="next" href="https://www.opengov.gr/home/category/consultations/page/4">»</a><a class="last" href="https://www.opengov.gr/home/category/consultations/page/60">Τελευταία »</a>
</div></div>
		</div>
	</div> """
]
# =================================================

# ---------------- Settings ----------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OpenGovCommentExporter/2.3)",
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9",
    "Accept-Language": "el,en;q=0.9",
}
TIMEOUT = 25
PAUSE   = 0.35            # polite pause between HTTP requests

# Comment crawling limits
MAX_COMMENT_PAGES   = 260       # safety cap per section for pagination pages
MAX_SINGLE_FETCHES  = 100000    # safety cap total for per-comment fallbacks
ENABLE_REST_FALLBACK = True     # try WP REST /wp-json/wp/v2/comments/<id> when needed

# Deduplication settings
DEDUP_SCOPE_GLOBAL = True       # True: remove duplicate texts across all sections; False: per-section only
KEEP_EMPTY_BODIES  = False      # if False, drop rows with empty comment body

# Reusable session + small cache
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
_URL_HTML_CACHE = {}  # url -> html

def fetch(url):
    """HTTP GET with small cache and polite delay."""
    if url in _URL_HTML_CACHE:
        return _URL_HTML_CACHE[url]
    time.sleep(PAUSE)
    r = SESSION.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    _URL_HTML_CACHE[url] = r.text
    return r.text

# ---------------- Utils ----------------
def strip_hash(url):
    u = urlsplit(url)
    return urlunsplit((u.scheme, u.netloc, u.path, u.query, ""))

def add_query_param(url, key, val):
    u = urlsplit(url)
    q = dict(parse_qsl(u.query, keep_blank_values=True))
    q[key] = str(val)
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q, doseq=True), u.fragment))

def html_to_text(s):
    return BeautifulSoup(s or "", "html.parser").get_text(" ", strip=True)

def normalize_text(s):
    """Normalize for dedupe: strip, collapse whitespace, lowercase, remove zero-width chars."""
    if not s:
        return ""
    t = html_to_text(s)
    t = re.sub(r"\s+", " ", t, flags=re.S).strip()
    t = t.replace("\u200b", "").replace("\ufeff", "")
    return t.lower()

def text_digest(s):
    return hashlib.sha1(normalize_text(s).encode("utf-8")).hexdigest()

# ------------- Step 1: parse consultations from INDEX HTML -------------
def parse_consultations_from_index(html_block):
    """
    Returns list of dicts: [{'Title','URL','Start_Date'}]
    Works with messy/indented or single-line HTML.
    """
    out = []
    soup = BeautifulSoup(html_block, "html.parser")
    listing_ul = (
        soup.select_one("div.index_listing div.downspace_item_content.archive_list > ul")
        or soup.select_one("div.index_listing .archive_list ul")
        or soup.select_one("div.archive_list > ul")
        or soup.select_one("ul")
    )
    if not listing_ul:
        return out

    for li in listing_ul.select("li"):
        a = li.select_one("p > a[href]")
        if not a:
            continue
        title = a.get_text(strip=True)
        url   = a["href"].strip()
        date_span = li.select_one("span.start")
        start_date = date_span.get_text(strip=True) if date_span else None
        out.append({"Title": title, "URL": url, "Start_Date": start_date})
    return out

# ------------- Step 2: parse sections list from consultation page -------------
def parse_sections_from_consultation_page(html, base_url):
    """
    Reads 'Πλοήγηση στη Διαβούλευση' list and returns:
      [{'title','url','post_id','count'}]
    """
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.select_one("ul.other_posts")
    if not ul:
        return []

    sections = []
    for li in ul.select("li"):
        sec_a = li.select_one("a.list_comments_link[href]")
        cnt_a = li.select_one("span.list_comments a[href]")
        if not sec_a or not cnt_a:
            continue

        title   = sec_a.get_text(strip=True)
        sec_url = urljoin(base_url, sec_a["href"].split("#", 1)[0])

        m_id = re.search(r"[?&]p=(\d+)", sec_url)
        post_id = int(m_id.group(1)) if m_id else None

        m_cnt = re.search(r"(\d+)", cnt_a.get_text(strip=True))
        count = int(m_cnt.group(1)) if m_cnt else 0

        sections.append({"title": title, "url": sec_url, "post_id": post_id, "count": count})
    return sections

# ------------- Step 3: discover & crawl ALL comment pages for a section -------------
def discover_comment_pagination(section_html, section_url):
    soup = BeautifulSoup(section_html, "html.parser")
    urls = set([strip_hash(section_url)])

    # Common WP pagination
    for a in soup.select("nav.comments-pagination a, .comment-navigation a, .pagination a, a.page-numbers"):
        href = a.get("href")
        if href:
            urls.add(strip_hash(urljoin(section_url, href)))

    # Regex fallback: comment-page-N or ?cpage=N
    for m in re.finditer(r'href=["\']([^"\']*(?:comment-page-\d+|[?&]cpage=\d+)[^"\']*)["\']', section_html, flags=re.I):
        urls.add(strip_hash(urljoin(section_url, m.group(1))))

    return urls

def crawl_all_comment_pages(start_url):
    pages = {}
    queue = [strip_hash(start_url)]
    seen  = set()

    while queue and len(seen) < MAX_COMMENT_PAGES:
        url = queue.pop(0)
        if url in seen:
            continue
        try:
            html = fetch(url)
        except requests.RequestException:
            continue

        pages[url] = html
        seen.add(url)

        for nxt in discover_comment_pagination(html, url):
            if nxt not in seen and nxt not in queue:
                queue.append(nxt)

    return pages

# ------------- Step 4: robust author/date/body extraction on list pages -------------
GREEK_MONTHS = r"(Ιανουάριος|Ιαν|Φεβρουάριος|Φεβ|Μάρτιος|Μαρ|Απρίλιος|Απρ|Μάιος|Μαι|Μάι|Ιούνιος|Ιουν|Ιούλιος|Ιουλ|Αύγουστος|Αυγ|Σεπτέμβριος|Σεπ|Οκτώβριος|Οκτ|Νοέμβριος|Νοε|Δεκέμβριος|Δεκ)"

def _clean_labelish(text):
    if not text:
        return None
    t = re.sub(r'\s*(?:λέει|says)\s*[:：]?\s*$', '', text.strip(), flags=re.I)
    t = re.sub(r'\b(?:Reply|Απάντηση)\b.*$', '', t, flags=re.I)
    return t.strip() or None

def _first_text(node):
    return (node.get_text(" ", strip=True) or None) if node else None

def _find_comment_permalink(comment_node, page_url, cid):
    """
    Try to capture the exact permalink inside this comment node:
      - a[href*="#comment-<cid>"] (preferred)
      - a[href*="?c=<cid>"] (single-comment view)
    Return absolute URL or None.
    """
    # Search inside the node first
    for sel in [
        f'a[href*="#comment-{cid}"]',
        f'a[href*="?c={cid}"]',
        'a[href*="#comment-"]',
        'a[href*="?c="]',
    ]:
        a = comment_node.select_one(sel)
        if a and a.get("href"):
            return urljoin(page_url, a["href"])

    # Regex fallback within this node's HTML
    html = str(comment_node)
    m = re.search(r'href=["\']([^"\']*(?:\?c=\d+|#comment-\d+))["\']', html, flags=re.I)
    if m:
        return urljoin(page_url, m.group(1))

    return None

def extract_author_generic(comment_node):
    for sel in [
        ".comment-author .fn a", ".comment-author .fn",
        ".vcard .fn a", ".vcard .fn",
        "cite.fn a", "cite.fn",
        "b.fn", "strong.fn",
        ".comment-author a[rel='author']",
        ".comment-author .url", "a.url",
        ".comment-author .author", ".comment-author .comment-author-link",
        ".comment-author", ".byline .author", ".byline",
        "header .fn", "header .author",
        ".comment-meta .author", ".comment-header .author",
        ".comment-author-name", ".author-name", ".commenter", ".comment-user"
    ]:
        n = comment_node.select_one(sel)
        if n:
            t = _clean_labelish(_first_text(n))
            if t:
                return t

    # Heuristic: leading "Name λέει:" / "Name says:"
    txt = comment_node.get_text(" ", strip=True)
    m = re.search(r"^\s*([^,|–—\-]+?)\s+(?:λέει|says)\b", txt, flags=re.I)
    if m:
        return _clean_labelish(m.group(1))

    # Bold first token
    first_strong = comment_node.find(["strong", "b"])
    if first_strong:
        t = _clean_labelish(first_strong.get_text(" ", strip=True))
        if t and 2 <= len(t) <= 100:
            return t

    # Legacy "Σχόλιο του χρήστη 'Name' | ..."
    m = re.search(r"Σχόλιο\s+του\s+χρήστη\s+['“”]?(.*?)['“”]?\s*\|", txt, flags=re.I)
    if m:
        return m.group(1).strip()

    return None

def extract_date_generic(comment_node, cid=None):
    t = comment_node.select_one("time[datetime]")
    if t and t.get("datetime"):
        return t["datetime"]

    for sel in [
        ".comment-metadata time", "a[rel='bookmark'] time",
        ".comment-meta time", ".commentmetadata time", "time",
        ".comment-date", ".comment_time", ".comment-time"
    ]:
        n = comment_node.select_one(sel)
        if n:
            txt = _first_text(n)
            if txt:
                return txt

    for sel in [".comment-meta.commentmetadata a", ".comment-meta a[href*='#comment-']", ".commentmetadata a"]:
        n = comment_node.select_one(sel)
        if n:
            txt = _first_text(n)
            if txt:
                return txt

    for sel in [".comment-meta", ".commentmetadata", ".comment-metadata", ".meta"]:
        n = comment_node.select_one(sel)
        if n:
            txt = _first_text(n)
            if txt:
                return txt

    # Regex within the node text (Greek month names / DMY forms)
    txt = comment_node.get_text(" ", strip=True)
    m = re.search(rf"\b(\d{{1,2}})\s+{GREEK_MONTHS}\s*,?\s*(\d{{4}})(?:\s*[–—\-]?\s*(\d{{1,2}}:\d{{2}}))?", txt, flags=re.I)
    if m:
        return m.group(0).strip()

    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})(?:\s+(\d{1,2}:\d{2}))?", txt)
    if m:
        return m.group(0).strip()

    return None

def extract_body_generic(comment_node):
    content = (
        comment_node.select_one(".comment-content") or
        comment_node.select_one(".comment-text") or
        comment_node.select_one(".entry-content") or
        comment_node.select_one(".comment-body") or
        comment_node
    )
    # remove non-body bits
    for bad in content.select(".reply, .comment-reply, .comment-meta, .commentmetadata, .comment-metadata"):
        bad.extract()

    paras = [p.get_text(" ", strip=True) for p in content.find_all("p")]
    if paras:
        return max(paras, key=len)
    # fall back to node-only text (not whole page)
    return content.get_text(" ", strip=True)

def parse_comment_dom_generic(comment_node, page_url):
    """
    Return (cid, author, date, body, permalink)
    """
    cid = None
    id_attr = (comment_node.get("id") or "").strip()
    if re.fullmatch(r"comment-\d+", id_attr):
        cid = id_attr.split("-", 1)[1]

    author = extract_author_generic(comment_node)
    date   = extract_date_generic(comment_node, cid=cid)
    body   = extract_body_generic(comment_node)
    permalink = _find_comment_permalink(comment_node, page_url, cid or "")
    return cid, author, date, body, permalink

def parse_all_comments_on_page(html, page_url):
    """
    STRICT: only nodes with id='comment-<digits>' to avoid grabbing page text.
    Skips pingbacks/trackbacks. Returns list of (cid, author, date, body, permalink).
    """
    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.select("li[id^='comment-'], div[id^='comment-'], article[id^='comment-']")
    nodes = [n for n in nodes if re.fullmatch(r"comment-\d+", (n.get('id') or '').strip())]

    def is_ping_or_trackback(node):
        cls = " ".join(node.get("class", [])).lower()
        return ("pingback" in cls) or ("trackback" in cls)

    out = []
    for n in nodes:
        if is_ping_or_trackback(n):
            continue
        cid, author, date_text, body, permalink = parse_comment_dom_generic(n, page_url)
        if cid and (author is not None or date_text is not None or body):
            out.append((cid, author, date_text, body, permalink))
    return out

# ------------- Step 5: per-comment fallbacks -------------
def parse_single_comment_page(html, cid=None):
    """
    Prefer li#comment-<cid>; fallback to legacy OpenGov "Σχόλιο του χρήστη ... | ..."
    """
    soup = BeautifulSoup(html, "html.parser")

    if cid:
        li = soup.select_one(f"#comment-{cid}")
        if li:
            _, author, date_text, body, _ = parse_comment_dom_generic(li, page_url="")
            if author or date_text or body:
                return author, date_text, body

    full = soup.get_text("\n", strip=True)
    m = re.search(r"Σχόλιο\s+του\s+χρήστη\s+['“”]?(.*?)['“”]?\s*\|\s*([^\n\r]+)", full, flags=re.I)
    author = m.group(1).strip() if m else None
    date_text = m.group(2).strip() if m else None

    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    body = max(paras, key=len) if paras else None
    return author or None, date_text or None, body or None

def build_single_comment_url(base_page_url, cid):
    base = strip_hash(base_page_url)
    base = re.sub(r"[?&]cpage=\d+", "", base)
    base = re.sub(r"[?&]c=\d+", "", base)
    return add_query_param(base, "c", cid)

def rest_fallback_for_comment(section_url, cid):
    """Try WP REST: /<site>/wp-json/wp/v2/comments/<cid> and /wp-json/wp/v2/comments/<cid>."""
    if not ENABLE_REST_FALLBACK:
        return None, None, None
    u = urlsplit(section_url)
    first_seg = "/" + (u.path.strip("/").split("/")[0] + "/" if u.path.strip("/") else "")
    candidates = [
        f"{u.scheme}://{u.netloc}{first_seg}wp-json/wp/v2/comments/{cid}",
        f"{u.scheme}://{u.netloc}/wp-json/wp/v2/comments/{cid}",
    ]
    for url in candidates:
        try:
            time.sleep(PAUSE)
            r = SESSION.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                try:
                    j = r.json()
                except Exception:
                    j = json.loads(r.text)
                if isinstance(j, dict):
                    author = j.get("author_name")
                    date   = j.get("date_gmt") or j.get("date")
                    content = j.get("content", {})
                    body = html_to_text(content.get("rendered")) if isinstance(content, dict) else None
                    return author, date, body
        except Exception:
            pass
    return None, None, None

# ------------------ main ------------------
def main():
    # 1) Parse the consultation index pages
    all_consultations = []
    for idx_html in html_index_pages:
        all_consultations.extend(parse_consultations_from_index(idx_html))

    # De-duplicate consultations by URL
    seen = set()
    consultations = []
    for c in all_consultations:
        if c["URL"] not in seen:
            seen.add(c["URL"])
            consultations.append(c)

    if not consultations:
        print("No consultations detected in the provided index HTML.")
        return

    print(f"Found {len(consultations)} consultation(s).")
    pd.DataFrame(consultations).to_excel("consultations_index.xlsx", index=False, engine="openpyxl")
    print("Saved consultations_index.xlsx")

    # 2) From each consultation, collect sections
    sections = []
    for row in consultations:
        url = row["URL"]
        try:
            html = fetch(url)
        except requests.RequestException as e:
            print(f"! Failed consultation GET: {url} ({e})")
            continue

        sec_list = parse_sections_from_consultation_page(html, url)
        if not sec_list:
            print(f"[Consultation] No 'Πλοήγηση στη Διαβούλευση' found: {url}")
            continue

        for s in sec_list:
            s2 = s.copy()
            s2["consultation_title"] = row["Title"]
            s2["consultation_date"]  = row["Start_Date"]
            sections.append(s2)

    if not sections:
        print("No sections found across consultations.")
        return

    # 3) Filter to sections that show >0 comments
    targets = [s for s in sections if s.get("count", 0) > 0]
    print(f"Sections with comments (announced): {len(targets)} / {len(sections)}")

    # 4) Crawl, extract, fallback, and export
    review_rows = []
    counter = 1
    single_fetches = 0
    dom_filled = 0
    fallback_filled = 0

    # Dedup: per-section and/or global, by normalized text digest
    global_text_seen = set()

    for sec in targets:
        # Crawl comment pagination
        try:
            pages = crawl_all_comment_pages(sec["url"])
        except Exception as e:
            print(f"! Pagination crawl failed for {sec['url']} ({e})")
            pages = {}

        # Map: cid -> [author, date, body, permalink]
        by_cid = {}

        # Parse all list pages
        for page_url, page_html in pages.items():
            parsed = parse_all_comments_on_page(page_html, page_url)
            for cid, author, date_text, body, permalink in parsed:
                if not cid:
                    continue
                if cid in by_cid:
                    old_a, old_d, old_b, old_p = by_cid[cid]
                    if not old_a and author: old_a = author
                    if not old_d and date_text: old_d = date_text
                    if not old_b or (body and len(body) > len(old_b)): old_b = body
                    if not old_p and permalink: old_p = permalink
                    by_cid[cid] = [old_a, old_d, old_b, old_p]
                else:
                    by_cid[cid] = [author, date_text, body, permalink]

        # Fallback for missing author/date/body per comment id
        for cid, vals in list(by_cid.items()):
            author, date_text, body, permalink = vals
            # If we already have everything, no fallback
            if author and date_text and body:
                dom_filled += 1
                continue
            if single_fetches >= MAX_SINGLE_FETCHES:
                continue

            # 1) Use the comment's own permalink (BEST)
            if permalink:
                try:
                    html_one = fetch(permalink)
                    fauthor, fdate, fbody = parse_single_comment_page(html_one, cid=cid)
                    if fauthor and not author: author = fauthor
                    if fdate and not date_text: date_text = fdate
                    if fbody and (not body or len(fbody) > len(body)): body = fbody
                except requests.RequestException:
                    pass

            # 2) If still missing, try the classic single-comment view ?c=<id>
            if (not author or not date_text) and (not permalink or "?c=" not in (permalink or "")):
                try:
                    single_url = build_single_comment_url(sec["url"], cid)
                    html_one = fetch(single_url)
                    fauthor, fdate, fbody = parse_single_comment_page(html_one, cid=cid)
                    if fauthor and not author: author = fauthor
                    if fdate and not date_text: date_text = fdate
                    if fbody and (not body or len(fbody) > len(body)): body = fbody
                except requests.RequestException:
                    pass

            # 3) WP REST fallback
            if (not author or not date_text) and ENABLE_REST_FALLBACK:
                rauthor, rdate, rbody = rest_fallback_for_comment(sec["url"], cid)
                if rauthor and not author: author = rauthor
                if rdate and not date_text: date_text = rdate
                if rbody and (not body or len(rbody) > len(body)): body = rbody

            by_cid[cid] = [author, date_text, body, permalink]
            if author or date_text or body:
                fallback_filled += 1
            single_fetches += 1

        # Build rows, dedupe by text
        section_text_seen = set()
        dup_dropped = 0
        kept = 0

        for cid, (author, date_text, body, _plink) in by_cid.items():
            # Skip empty bodies if configured
            if not body and not KEEP_EMPTY_BODIES:
                continue

            digest = text_digest(body or "")
            if DEDUP_SCOPE_GLOBAL:
                already = (digest in global_text_seen)
            else:
                already = (digest in section_text_seen)

            if already:
                dup_dropped += 1
                continue

            # Mark as seen
            if DEDUP_SCOPE_GLOBAL:
                global_text_seen.add(digest)
            else:
                section_text_seen.add(digest)

            review_rows.append({
                "Comment_Number": counter,
                "User_Name": author or "",
                "Consultation_Title": f"{sec['consultation_title']}",
                "Section_Title": f"{sec['title']}",
                "Comment_Date": date_text or "",
                "Comment_Text": body or "",
            })
            kept += 1
            counter += 1

        print(f"\n[Section] {sec['title']}  • expecting ~{sec['count']}")
        print(f"  - Pages crawled: {len(pages)}")
        print(f"  - Unique comment IDs parsed: {len(by_cid)}")
        print(f"  - Comments kept after de-dup (by text): {kept}")
        print(f"  - Duplicates removed (by text): {dup_dropped}")

    # 5) Export comments
    if review_rows:
        df = pd.DataFrame(review_rows)
        df.to_excel("opengov_comments.xlsx", index=False, engine="openpyxl")
        print(f"\nSaved {len(df)} rows to opengov_comments.xlsx")
        print(f"Filled via DOM (complete rows): {dom_filled} | Filled via fallbacks (permalink/?c=/REST): {fallback_filled} | Fallback requests used: {single_fetches}")
    else:
        print("\nNo comments found after crawling and deduping.")

if __name__ == "__main__":
    main()