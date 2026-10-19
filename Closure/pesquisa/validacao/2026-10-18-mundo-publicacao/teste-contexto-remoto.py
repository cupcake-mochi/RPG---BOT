import sys
sys.path.insert(0,"ferramentas/prompt_do_site")
import site_prompt
casos=[("Como chego em Victoria?","ferrovia capaz de atravessar"),("Como acesso Aegir?","pressurizada"),("Qual a capital de Columbia?","Max D.C."),("Ja chegaram na Lua?","Lua"),("Como funciona a promocao de Grau?","nao seja PJ"),("Qual e a cura da Oripatia?","cura conhecida")]
for pers in ("kal","clo"):
 for q, trecho in casos:
  p=site_prompt.montar(pers,q,hora=(14,0),motor="quickjs")
  import unicodedata
  normal=lambda s:"".join(c for c in unicodedata.normalize("NFD",s.lower()) if unicodedata.category(c)!="Mn")
  assert normal(trecho) in normal(p["input"][-1]["content"]),(pers,q)
  assert p["versoes"]["mundo"]=="era-2026-10-18-v1"
  print("PASS",pers,q)
print("RESULTADO: 12/12; motor QuickJS da hospedagem; nenhuma chamada de modelo")
