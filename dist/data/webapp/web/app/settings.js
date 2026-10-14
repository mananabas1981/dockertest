// appHome.setContent(SettingView, "Setting");
import { Panel, Button, BasicTab } from "./plugin/mcontrol.js";
import { SettingDepartmentPage } from "./settings/page_setting.js";
import { PageSignatory } from "./settings/page_signatory.js";
import { PageDeduction } from "./settings/deduction.js";
import { PageSystemSetting } from "./settings/page_setting.js";
import { CompanyBankInformation } from "./settings/page_setting.js";
import { BankList } from "./settings/bank_list.js";
import { SystemAccess } from "./settings/system_access.js";
import ChargedPage from "./settings/charged.js";

import { DigitalSignaturePage } from './component/Signature.js';

export function SettingView() {

  const mainPanel = new Panel();

  // var panel = new Panel();
  // panel.addClass("btn-group");
  // panel.control.style.padding = "10px";
  // var dept = new Button("Department", "secondary", "home", "Department");
  // var charges = new Button("Charges", "secondary", "refresh", "Funding or Charges setting");
  // var sign = new Button("Signatory", "secondary", "cog", "Signatory");
  // var ded = new Button("Compensation|Deduction", "secondary", "money", "Deduction list");
  // var system = new Button("System", "secondary", "cogs", "System Setting");
  // var bank_info = new Button('Company Bank', 'secondary', 'home', 'Company bank information!');

  // var bank_type = new Button("Bank List", "secondary", "home", "Click to add bank for payroll");

  // var sys_access = new Button("System Access", "secondary", "cogs", "click to view all the access");
  // const sign_btn = new Button('Digital Signature', 'secondary', 'pencil');



  // var contentPanel = new Panel();
  // contentPanel.control.style.padding = "10px";

  // sign.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(new PageSignatory());
  // });

  // ded.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(new PageDeduction());
  // });

  // system.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(new PageSystemSetting());
  // });

  // bank_info.addEventListener('click', function () {
  //   contentPanel.clear();
  //   contentPanel.add(new CompanyBankInformation());
  // });

  // dept.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(new SettingDepartmentPage());
  // });

  // bank_type.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(BankList());
  // });

  // sys_access.addEventListener("click", function () {
  //   contentPanel.clear();
  //   contentPanel.add(new SystemAccess().container());
  // });

  // sign_btn.addEventListener('click', () => {
  //   contentPanel.clear();
  //   contentPanel.add(new DigitalSignaturePage());
  // });

  // charges.addEventListener("click", () => {
  //   contentPanel.clear();
  //   contentPanel.add(new ChargedPage());
  // });

  // panel.add(dept);
  // panel.add(charges);
  // panel.add(sign);
  // panel.add(ded);
  // panel.add(system);
  // panel.add(bank_info);
  // panel.add(bank_type);
  // panel.add(sys_access);
  // panel.add(sign_btn);

  // mainPanel.add(panel);
  // mainPanel.add(contentPanel);

  const tab = new BasicTab();
  
  tab.add("Department", o => {
    o.add(new SettingDepartmentPage());
  }, true);

  tab.add("Charges", o => {
    o.add(new ChargedPage());
  });

  tab.add("Signatory", o => {
    o.add(new PageSignatory());
  });

  tab.add("Deduction", o => {
    o.add(new PageDeduction());
  });

  tab.add("System", o => {
    o.add(new PageSystemSetting());
  });

  tab.add("Bank Info", o => {
    o.add(new CompanyBankInformation());
  });

  tab.add("Bank List", o => {
    o.add(new BankList());
  });

  tab.add("Access", o => {
    o.add(new SystemAccess().container());
  });

  tab.add("Digital Signature", o => {
    o.add(new DigitalSignaturePage());
  });

  mainPanel.add(new Panel().add(tab).setStyle({
    padding: "10px"
  }));

  return mainPanel;
};