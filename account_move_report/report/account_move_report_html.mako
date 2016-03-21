<html>
    <head>
        <style type="text/css">
            ${css}
            table {
    border-collapse: separated;

}
            table, .th, .td {
    border: 2px solid white;
}
    table.basic_table{
    text-align:left;
    }

    .celdaTotal{
    font-size:8pt;
    font-style:normal;
    font-family: FreeMono;
    text-align:right;
    font-weight:bold;
    background-color:#dcdcdc;
    }

    .celdaDetailTitulo{
    font-style:italic;
    font-size:10pt;
    text-align:left;
    font-family:Arial,Helvetica,sans-serif;
    }

    .celdaDetail{
    font-size:7pt;
    font-family: monospace;
    background-color:#F5F5F5;
    text-align:left;
    }

    .celdaTituloTabla{
    font-size:7pt;
    text-align:center;
    font-family:Arial,Helvetica,sans-serif;
    font-weight: bold;
    background-color:#620400;
    color:#FFFFFF;
    }

    div.td_company
    {
    font-size:12pt;
    margin-left:0;
    font-weight:bold;
    font-family:Arial,Helvetica,sans-serif;
    }

    div.td_company_title
    {
    font-size:22pt;
    margin-left:0;
    font-weight:bold;
    font-family:Arial,Helvetica,sans-serif;
    }
        </style>
    </head>
    <body>
        %for o in objects :
        <table width = '100%' class='td_company_title'>
            <tr>
                <td style="vertical-align: top;max-height: 45px;" width= '30%'>
                    ${helper.embed_image('jpeg',str(o.company_id.logo),95, 95)}
                </td>
                <td width= '40%'>
                    <div>${o.company_id.name or ''|entity}</div>
                    <br>${o.company_id.partner_id.street or ''|entity} No. 
                                                ${o.company_id.partner_id.street2 or ''|entity}
                                                ${o.company_id.partner_id.zip or ''|entity}
                                                <br/>${o.company_id.partner_id.city or ''|entity}
                                                , ${o.company_id.partner_id.state_id.name or ''|entity}
                                                , ${o.company_id.partner_id.country_id.name or ''|entity}
                </td>
                <td width= '30%' class='celdaDetailTitulo'>
                    <div>${_("Printing Date:")} ${time.strftime('%d/%m/%Y %H:%M:%S',time.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))}</div>
                </td>
            </tr>
        </table>                                   

        <table width= '100%' class='celdaDetailTitulo'>
            <tr>
                <div>
                    <td style="width: 50%">${_("Comprobante: ")} ${o.name or '' |entity}</td>
                    <td style="width: 50%;font-weight:bold;font-size:13pt;">${get_title(o.line_id) |entity}</td>
                </div>
            </tr>
            <tr>
                <div>
                    <td>${_("Reference: ")} ${o.ref or '' |entity}</td>
                </div>
            </tr>
            <tr>
                <div>
                    <td width= '50%'>
                        ${_("Period: ")} ${o.period_id.name or '' |entity}
                    </td>
                    <td width= '50%'>
                        ${_("Date: ")} ${time.strftime('%d/%m/%Y',time.strptime(o.date, '%Y-%m-%d')) or '' |entity}
                    </td>  
                </div>
            </tr>
            <tr>
                <div>
                    <tr>
                        <td colspan="2">
                            ${_("Glosa General: ")}
                            ${get_note(o.id)[0] |entity}
                        </td>
                    </tr>
                </div>
            </tr>
        </table>
        
        <table width= '100%' style="border-collapse: collapse;">
            <tr class='celdaTituloTabla'>
                <td width='5%'>
                    <div>${_("Invoice")}</div>
                </td>
                <td width='7%'>
                    <div>${_("Name")}</div>
                </td>
                <td width='14%'>
                    <div>${_("Partner")}</div>
                </td>
                <td width='20%'>
                    <div>${_("Account")}</div>
                </td>
                <td width='14%'>
                    <div>${_("Due date")}</div>
                </td>
                <td width='8%'>
                    <div>${_("Debit")}</div>
                </td>
                <td width='8%'>
                    <div>${_("Credit")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Amount Currency")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Currency")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Reconcile")}</div>
                </td>
                <td width='6%'>
                    <div>${_("Partial Reconcile")}</div>
                </td>
            </tr>
            %for line in o.line_id:
            <tr class='celdaDetail'>
                <td width='5%'>
                    <div>${line.invoice.number or '' |entity}</div>
                </td>
                <td width='7%' style="word-wrap: break-word">
                    <div>${line.name or '' |entity}</div>
                </td>
                <td width='14%'>
                    <div>${line.partner_id.name or ''}</div>
                </td>
                <td width='10%'>
                    <div>${line.account_id.code or '' |entity} - ${line.account_id.name or '' |entity}</div>
                </td>
                <td width='14%'>
                    <div>${line.date_maturity or '' |entity}</div>
                </td>
                <td width='8%' style="text-align:right;">
                    <div>${formatLang(line.debit or 0.0) |entity}</div>
                </td>
                <td width='8%' style="text-align:right;">
                    <div>${formatLang(line.credit or 0.0) |entity}</div>
                </td>
                <td width='16%' style="text-align:right;">
                    <div>${formatLang(line.amount_currency or 0.0) |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.currency_id.name or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.reconcile_id.name or '' |entity}</div>
                </td>
                <td width='6%'>
                    <div>${line.reconcile_partial_id.name or '' |entity}</div>
                </td>
            </tr>
            %endfor
            <tr class='celdaTotal'>
                <td colspan="5"></td>
                <td>
                    <div width='6%' >${formatLang(get_total_debit_credit(o.line_id)['sum_tot_debit'] or 0.0) |entity}</div>
                </td>
                <td>
                    <div width='6%'>${formatLang(get_total_debit_credit(o.line_id)['sum_tot_credit'] or 0.0) |entity}</div>
                </td>
                <td colspan="9"></td>
            </tr>
            <tr  class='celdaDetailTitulo'>
                <td colspan="2">
                    ${_("Detalle: ")}
                    ${get_note(o.id)[1] |entity}
                </td>
            </tr>
            
        </table>
        <br/>
        <br/>
        <br/>
        <br/>
        <table width= '100%'>
            <tr>
                <td style="border-top: 1px solid #000;width: 20%;text-align: center;font-size:8pt;">
                    Realizado Por
                </td>
                <td style="width: 5%;"></td>
                <td style="border-top: 1px solid #000;width: 20%;text-align: center;font-size:8pt;">
                    Revizado Por
                </td>
                <td style="width: 5%;"></td>
                <td style="border-top: 1px solid #000;width: 20%;text-align: center;font-size:8pt;">
                    Autorizado Por
                </td>
                <td style="width: 5%;"></td>
                <td style="border-top: 1px solid #000;width: 20%;text-align: center;font-size:8pt;">
                    Pagado a / Recibido de
                </td>

            </tr>
        </table>
    %endfor
    </body>
</html>
