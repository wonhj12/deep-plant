import * as XLSX from 'xlsx';
import { apiIP } from "../../config";

// export 할 육류 데이터 목록 fetch
const getDataListJSON = async () => {
    const json = await (
        await fetch(`http://${apiIP}/meat/get`)
    ).json();
   return json;
};

// JSON파일을 엑셀로 변환하기
const downloadExcel = (data) => {
    const rows = DataListJSON2Excel(data);
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'my_sheet');
    XLSX.writeFile(workbook, '데이터목록.xlsx');
};


// json 데이터 가공
const DataListJSON2Excel = (rawData) => {
    let newData = [];
    // row
    for(var row in rawData){
        newData = [
            ...newData,
            rawData[row]
        ];
    }
    return newData;
}

export {getDataListJSON, downloadExcel};