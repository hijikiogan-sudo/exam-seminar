from pathlib import Path
import hashlib,json,shutil,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import ROOT,read_session,build

class ReleaseValidation(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)/'2026-09-19'
  shutil.copytree(ROOT/'content'/'2026-09-19',self.folder)
 def tearDown(self):self.tmp.cleanup()
 def metadata(self):return json.loads((self.folder/'session.json').read_text())
 def save(self,m):(self.folder/'session.json').write_text(json.dumps(m,ensure_ascii=False))
 def change(self,name,text,review=False):
  p=self.folder/name;p.write_text(text)
  if review:
   m=self.metadata();m['review']['sha256'][name]=hashlib.sha256(text.encode()).hexdigest();self.save(m)
 def test_reviewed_session_accepted(self):self.assertEqual(read_session(self.folder)[0]['date'],'2026-09-19')
 def test_changed_after_review_rejected(self):
  p=self.folder/'english.html';self.change(p.name,p.read_text()+'\n')
  with self.assertRaisesRegex(ValueError,'確認後に変更'):read_session(self.folder)
 def test_private_email_rejected_even_with_matching_hash(self):
  p=self.folder/'english.html';self.change(p.name,p.read_text()+'<p>student@example.com</p>',True)
  with self.assertRaisesRegex(ValueError,'個人情報候補'):read_session(self.folder)
 def test_embedded_script_rejected(self):
  p=self.folder/'english.html';self.change(p.name,p.read_text()+'<script>alert(1)</script>',True)
  with self.assertRaisesRegex(ValueError,'タグ'):read_session(self.folder)
 def test_missing_subject_rejected(self):
  m=self.metadata();del m['themes']['science'];self.save(m)
  with self.assertRaisesRegex(ValueError,'5教科'):read_session(self.folder)
 def test_identical_math_rejected(self):
  self.change('math-practice.html',(self.folder/'math-summary.html').read_text(),True)
  with self.assertRaisesRegex(ValueError,'同一'):read_session(self.folder)
 def test_duplicate_ids_rejected(self):
  p=self.folder/'english.html';self.change(p.name,p.read_text()+'<p id="duplicate">a</p><p id="duplicate">b</p>',True)
  with self.assertRaisesRegex(ValueError,'重複ID'):read_session(self.folder)
 def test_existing_output_never_overwritten(self):
  out=Path(self.tmp.name)/'output';out.mkdir();(out/'keep').write_text('keep')
  with self.assertRaisesRegex(ValueError,'上書きせず'):build(out)
  self.assertEqual((out/'keep').read_text(),'keep')

if __name__=='__main__':unittest.main()
