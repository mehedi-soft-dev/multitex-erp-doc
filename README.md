# Knowledge Graph Example — Payment Mode

## Payment Mode — এখন সম্পূর্ণ গ্রাফ কেমন দেখতে

```
mod:accounting
   │
   └──CONTAINS──► feat:acc-payment-mode  (মূল Feature)
                       │
                       ├──USES_SERVICE──► svc:PaymentModeService
                       │
                       ├──EXPOSES──► mvc:PaymentModeController.Index   (পেজ শেল)
                       │
                       ├──EXPOSES──► api:GET:.../get-payment-modes  ──INJECTS──► svc:PaymentModeService
                       ├──EXPOSES──► api:POST:.../save-payment-mode ──INJECTS──► svc:PaymentModeService
                       ├──EXPOSES──► api:PUT:.../update-payment-mode──INJECTS──► svc:PaymentModeService
                       ├──EXPOSES──► api:GET:.../get-payment-mode   ──INJECTS──► svc:PaymentModeService
                       ├──EXPOSES──► api:DELETE:.../delete-payment-mode──INJECTS──► svc:PaymentModeService
                       │
                       ├──CALLS──► proc:ac_payment_mode_select
                       ├──CALLS──► proc:ac_payment_mode_select_by_Id
                       ├──CALLS──► proc:ac_payment_mode_delete
                       ├──CALLS──► proc:acc_payment_mode_insert
                       │
                       └──USES_TABLE──► tbl:ACC_PAYMENT_MODE
                                        tbl:ACC_VOUCHER_MASTER
                                        tbl:ACC_MAP_PAY_MODE

col:ACC_VOUCHER_MASTER.PAYMENT_MODE_ID ──FK_TO──► col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID
col:ACC_MAP_PAY_MODE.PAYMENT_MODE_ID   ──FK_TO──► col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID
```

## AI agent কিভাবে এটা ব্যবহার করবে — একটা বাস্তব উদাহরণ

ধরো তুমি agent-কে বললে: **"Payment Mode delete করলে ঠিকভাবে কাজ করছে কিনা check করো"**

Agent কী করবে, ধাপে ধাপে:

1. **কোথা থেকে শুরু করবে?** → `feat:acc-payment-mode` node খুঁজবে
2. **কোন API endpoint delete করে?** → `EXPOSES` edge অনুসরণ করে পাবে: `api:DELETE:.../delete-payment-mode`
3. **কোন C# method এটা handle করে?** → ঐ node-এর `handler` field-এ লেখা আছে: `PaymentModesController.DeletePaymentMode`
4. **কোন service ব্যবহার হয়?** → `INJECTS` edge অনুসরণ করে পাবে: `svc:PaymentModeService`
5. **কোন stored procedure আসল কাজটা করে?** → `CALLS` edge থেকে পাবে: `proc:ac_payment_mode_delete`
6. **এই delete করলে অন্য কোথায় প্রভাব পড়বে?** → `col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID`-কে যারা `FK_TO` দিয়ে point করছে তাদের খুঁজবে — পাবে `ACC_VOUCHER_MASTER` আর `ACC_MAP_PAY_MODE`
7. এবার agent শুধু **৩-৪টা নির্দিষ্ট ফাইল** খুলে দেখবে (Controller, Service, Procedure, আর ঐ দুইটা table) — পুরো codebase grep করা লাগলো না

**মূল কথা:** আগে agent-কে অনুমান করে করে খুঁজতে হতো "কোথায় শুরু করব", এখন গ্রাফ সরাসরি **route বলে দেয়** — feature থেকে শুরু করে API → Service → Procedure → Table → Column, প্রতিটা ধাপ এক লাইনে জানা যায়।

## Raw graph data (from `.agent/knowledge-graph/nodes.jsonl` and `edges.jsonl`)

### Nodes

```json
{"id": "feat:acc-payment-mode", "type": "Feature", "source_file": "docs\\accounting\\features\\payment-mode.md", "status": "verified", "http": null, "module": "accounting", "category": "master-data"}
{"id": "svc:PaymentModeService", "type": "Service", "source_file": "docs\\accounting\\features\\payment-mode.md", "name": "PaymentModeService"}
{"id": "mvc:PaymentModeController.Index", "type": "MvcAction", "source_file": "docs\\accounting\\features\\payment-mode.md", "handler": "PaymentModeController.Index"}
{"id": "api:GET:api/accounting/payment-modes/get-payment-modes", "type": "ApiAction", "method": "GET", "path": "api/accounting/payment-modes/get-payment-modes", "handler": "PaymentModesController.GetPayementModes"}
{"id": "api:POST:api/accounting/payment-modes/save-payment-mode", "type": "ApiAction", "method": "POST", "path": "api/accounting/payment-modes/save-payment-mode", "handler": "PaymentModesController.SavePaymentMode"}
{"id": "api:PUT:api/accounting/payment-modes/update-payment-mode", "type": "ApiAction", "method": "PUT", "path": "api/accounting/payment-modes/update-payment-mode", "handler": "PaymentModesController.UpdateCompany"}
{"id": "api:GET:api/accounting/payment-modes/get-payment-mode", "type": "ApiAction", "method": "GET", "path": "api/accounting/payment-modes/get-payment-mode", "handler": "PaymentModesController.GetPaymentMode"}
{"id": "api:DELETE:api/accounting/payment-modes/delete-payment-mode", "type": "ApiAction", "method": "DELETE", "path": "api/accounting/payment-modes/delete-payment-mode", "handler": "PaymentModesController.DeletePaymentMode"}
{"id": "tbl:ACC_PAYMENT_MODE", "type": "Table", "status": "inferred", "module": "accounting"}
{"id": "col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID", "type": "Column", "table": "tbl:ACC_PAYMENT_MODE"}
{"id": "col:ACC_VOUCHER_MASTER.PAYMENT_MODE_ID", "type": "Column", "table": "tbl:ACC_VOUCHER_MASTER"}
{"id": "col:ACC_MAP_PAY_MODE.PAYMENT_MODE_ID", "type": "Column", "table": "tbl:ACC_MAP_PAY_MODE"}
{"id": "col:ACC_MAP_PAY_MODE.VOUCHERT_TYPE_ID", "type": "Column", "table": "tbl:ACC_MAP_PAY_MODE"}
```

### Edges

```json
{"from": "mod:accounting", "to": "feat:acc-payment-mode", "type": "CONTAINS"}
{"from": "feat:acc-payment-mode", "to": "svc:PaymentModeService", "type": "USES_SERVICE"}
{"from": "feat:acc-payment-mode", "to": "mvc:PaymentModeController.Index", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "api:GET:api/accounting/payment-modes/get-payment-modes", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "api:POST:api/accounting/payment-modes/save-payment-mode", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "api:PUT:api/accounting/payment-modes/update-payment-mode", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "api:GET:api/accounting/payment-modes/get-payment-mode", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "api:DELETE:api/accounting/payment-modes/delete-payment-mode", "type": "EXPOSES"}
{"from": "feat:acc-payment-mode", "to": "proc:ac_payment_mode_select", "type": "CALLS"}
{"from": "feat:acc-payment-mode", "to": "proc:ac_payment_mode_select_by_Id", "type": "CALLS"}
{"from": "feat:acc-payment-mode", "to": "proc:ac_payment_mode_delete", "type": "CALLS"}
{"from": "feat:acc-payment-mode", "to": "proc:acc_payment_mode_insert", "type": "CALLS"}
{"from": "feat:acc-payment-mode", "to": "tbl:ACC_PAYMENT_MODE", "type": "USES_TABLE"}
{"from": "feat:acc-payment-mode", "to": "tbl:ACC_VOUCHER_MASTER", "type": "USES_TABLE"}
{"from": "feat:acc-payment-mode", "to": "tbl:ACC_MAP_PAY_MODE", "type": "USES_TABLE"}
{"from": "col:ACC_VOUCHER_MASTER.PAYMENT_MODE_ID", "to": "col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID", "type": "FK_TO"}
{"from": "col:ACC_MAP_PAY_MODE.PAYMENT_MODE_ID", "to": "col:ACC_PAYMENT_MODE.PAYMENT_MODE_ID", "type": "FK_TO"}
```

> Note: `voucher.md` also independently exposes `api:GET:api/accounting/voucher-masters/get-payment-modes`
> (`VoucherMastersController.GetPaymentModes`) — a second, separate endpoint that also reads
> payment modes. Not shown in the diagram above since it belongs to the Voucher feature, not
> Payment Mode itself.
