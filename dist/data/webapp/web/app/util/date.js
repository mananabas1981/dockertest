const month_config = [
  'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
];

export const date_string1 = (dt) => {
  const [year, month, day] = dt.split('-');


  return `${month_config[parseInt(month) - 1]} ${day}, ${year}`;
};