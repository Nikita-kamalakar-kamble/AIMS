SELECT ext.brand, ext.brand_name, ext.entity_code,
                                   ext.entity_desc, ext.invoice_number, ext.invoice_date,
                                   ext.customer_code, ext.customer_name, ext.customer_site, ext.customer_site_name, ext.currency, ext.total_value,
                                   ext.article_code, ext.article_desc,  ext.article_note, ext.total_value1,
                                   ext.vat_percentage, ext.vat_amount, ext.status, ext.remark, ext.shipment_ref,
                                   ext.createdon, ext.createdby, ext.cancelledby, ext.cancelledon, ext.cancel_reason, ext.credit_note FROM (
                            SELECT    mh.brand,
                                                          (SELECT MAX(brand_name) from brand where brand = mh.brand) brand_name,
                                                          mh.entity_code,
                                                                                        mh.entity_desc,
                                                                                        mh.invoice_number,
                                                                                        CASE WHEN mh.invoice_status = 'D' AND INSTR(mh.invoice_number,'FOC') = 0 THEN
                                                                                        mh.cancelledon
                                                                                        ELSE
                                                                                        mh.invoice_date
                                                                                        END invoice_date    ,
                                                                                        (SELECT customer
                                                                                             FROM miscinv_customer
                                                                                          WHERE customer_id = mh.customer_id) customer_code,
                                                                                        (SELECT customer_name
                                                                                             FROM miscinv_customer
                                                                                          WHERE customer_id = mh.customer_id) customer_name,
                                                                                        mh.customer_site   ,
                                                                                        (SELECT customer_site_name
                                                                                             FROM miscinv_customer_site
                                                                                          WHERE customer_id = mh.customer_id
                                                                                                  AND customer_site = mh.customer_site) customer_site_name,
                                                                                        mh.currency           ,
                                                                                        mh.total_value        ,
                                                                                        md.article_code      ,
                                                                                        md.article_desc      ,
                                                                                        md.article_note      ,
                                                                                        NVL(md.total_value,0)  -  NVL(md.vat_amount,0) total_value1 ,
                                                                                        md.vat_percentage ,
                                                                                        md.vat_amount       ,
                                                                                        CASE WHEN INSTR(mh.invoice_number,'FOC') <> 0 THEN
                                                                                        'Confirmed'
                                                                                        ELSE
                                                                                        (SELECT description
                                                                                            FROM inv_status_v
                                                                                          WHERE code = mh.invoice_status)
                                                                                        END  status ,
                                                                                        mh.remark, mh.shipment_ref,
                                                          mh.createdon,
                                                          mh.createdby,
                                                          mh.cancelledby,
                                                          mh.cancelledon,
                                                          mh.cancel_reason,
                                                          mh.credit_note
                                                  FROM miscinv_header mh, miscinv_detail md
                                                 WHERE mh.invoice_id  = md.invoice_id(+)
                            Union all
                            SELECT    mh.brand,
                                                          (SELECT MAX(brand_name) from brand where brand = mh.brand) brand_name,
                                                          mh.entity_code,
                                                                                        mh.entity_desc,
                                                                                        mh.invoice_number,
                                                                                        mh.invoice_date     ,
                                                                                        (SELECT customer
                                                                                             FROM miscinv_customer
                                                                                          WHERE customer_id = mh.customer_id) customer_code,
                                                                                        (SELECT customer_name
                                                                                             FROM miscinv_customer
                                                                                          WHERE customer_id = mh.customer_id) customer_name,
                                                                                        mh.customer_site   ,
                                                                                        (SELECT customer_site_name
                                                                                             FROM miscinv_customer_site
                                                                                          WHERE customer_id = mh.customer_id
                                                                                                  AND customer_site = mh.customer_site) customer_site_name,
                                                                                        mh.currency           ,
                                                                                        mh.total_value        ,
                                                                                        md.article_code      ,
                                                                                        md.article_desc      ,
                                                                                        md.article_note      ,
                                                                                        NVL(md.total_value,0)  -  NVL(md.vat_amount,0) total_value1 ,
                                                                                        md.vat_percentage ,
                                                                                        md.vat_amount       ,
                                                                                        CASE WHEN INSTR(mh.invoice_number,'FOC') <> 0 THEN
                                                                                        'Confirmed'
                                                                                        ELSE
                                                                                        (SELECT description
                                                                                            FROM inv_status_v
                                                                                          WHERE code = 'C')
                                                                                        END  status ,
                                                                                        mh.remark,  mh.shipment_ref,
                                                          mh.createdon,
                                                          mh.createdby,
                                                          NULL cancelledby,
                                                          NULL cancelledon,
                                                          NULL cancel_reason,
                                                          mh.credit_note
                                                  FROM miscinv_header mh, miscinv_detail md
                                                 WHERE mh.invoice_id  = md.invoice_id(+)
                                                   AND mh.invoice_status = 'D'
                                                   AND mh.invoice_number  not like '%FOC%'
                              )  ext
                              ORDER BY ext.brand,ext.entity_code,ext.invoice_date