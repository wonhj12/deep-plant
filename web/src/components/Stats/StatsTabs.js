import { useState } from "react"
import PropTypes from 'prop-types';
import { Tabs, Tab, Box, Button, useTheme } from '@mui/material';
import BarGraph from "./Charts/barGraph";
import PieChart from "./Charts/pieChart";
import AreaChart from "./Charts/BoxPlot/Sens_FreshMeat";
import { IoBarChart, IoPieChart } from "react-icons/io5";
import Typography from "@mui/material/Typography";
import * as React from "react";
import { Select, MenuItem } from '@mui/material';
import Sens_FreshMeat from "./Charts/BoxPlot/Sens_FreshMeat";
import Sens_ProcMeat from "./Charts/BoxPlot/Sens_ProcMeat";
import Sens_HeatedMeat from "./Charts/BoxPlot/Sens_HeatedMeat";
import Taste_FreshMeat from "./Charts/BoxPlot/Taste_FreshMeat";
import Taste_ProcMeat from "./Charts/BoxPlot/Taste_ProcMeat";
import Sens_Fresh_Map from "./Charts/HeatMap/Sens_Fresh_Map";
import Sens_Heated_Map from "./Charts/HeatMap/Sens_Heated_Map";
import Taste_Fresh_Map from "./Charts/HeatMap/Taste_Fresh_Map";
import Taste_Proc_Map from "./Charts/HeatMap/Taste_Proc_Map";
import Taste_Time from "./Charts/Time/Taste_Time";
import { useEffect } from "react";
import Sens_Proc_Map from "./Charts/HeatMap/Sens_Proc_Map";
import Taste_Fresh_Corr from "./Charts/Corr/Taste_Fresh_Corr";
import Sense_Proc_Corr from "./Charts/Corr/Sense_Proc_Corr";
import Sense_Heated_Corr from "./Charts/Corr/Sense_Heated_Corr";
import Sense_Fresh_Corr from "./Charts/Corr/Sense_Fresh_Corr";
import Taste_Proc_Corr from "./Charts/Corr/Taste_Proc_Corr";
function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
      style={{ backgroundColor: "white" }}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`,
  };
}

export default function StatsTabs({ startDate, endDate }) {
  const [value, setValue] = useState(0);
  const [slot, setSlot] = useState("week");
  useEffect(() => { console.log('stat tab' + startDate, '-', endDate) }, [startDate, endDate]);
  const theme = useTheme();
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };


  const [alignment, setAlignment] = React.useState("맛");
  const [secondary, setSecondary] = React.useState("원육");

  const handleFirstChange = (event) => {
    setAlignment(event.target.value);
    setSecondary("원육"); // Initialize secondary to "원육"
  };

  const handleSecondChange = (event) => {
    setSecondary(event.target.value);
  };

  return (
    <Box sx={{ width: "900px", height: "350px" }}>

      <Box
        sx={{
          borderBottom: 1,
          borderColor: "divider",
          backgroundColor: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Tabs
          value={value}
          onChange={handleChange}
          textColor="secondary"
          indicatorColor="secondary"
        >
          <Tab label="통계" {...a11yProps(0)} />
          <Tab label="분포" {...a11yProps(1)} />
          <Tab label="상관관계" {...a11yProps(2)} />
          <Tab label="시계열" {...a11yProps(3)} />
        </Tabs>
        <Box>

          {value !== 3 && (
            <div>
              <Select
                labelId="alignment-label"
                id="alignment"
                value={alignment}
                onChange={handleFirstChange}
                label="맛 또는 관능"
              >
                <MenuItem value="맛">맛</MenuItem>
                <MenuItem value="관능">관능</MenuItem>
              </Select>
              <Select
              labelId="secondary-label"
              id="secondary"
              value={secondary}
              onChange={handleSecondChange}
              label="원육, 처리육, 가열육"
            >
              <MenuItem value="원육">원육</MenuItem>
              <MenuItem value="처리육">처리육</MenuItem>
              {alignment === "관능" && (
                <MenuItem value="가열육">가열육</MenuItem>
              )}
            </Select>
            </div>
          )}

        </Box>

      </Box>
      {/* BoxPlot(통계) */}
      <CustomTabPanel value={value} index={0}>
        {alignment === "관능" && secondary === "원육" ? (
          <Sens_FreshMeat startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "처리육" ? (
          <Sens_ProcMeat startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "가열육" ? (
          <Sens_HeatedMeat startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "원육" ? (
          <Taste_FreshMeat startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "처리육" ? (
          <Taste_ProcMeat startDate={startDate} endDate={endDate} />
        ) : null}
      </CustomTabPanel>

      {/* HeatMap(분포) */}
      <CustomTabPanel value={value} index={1}>
        {alignment === "관능" && secondary === "원육" ? (
          <Sens_Fresh_Map startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "처리육" ? (
          <Sens_Proc_Map startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "가열육" ? (
          <Sens_Heated_Map startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "원육" ? (
          <Taste_Fresh_Map startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "처리육" ? (
          <Taste_Proc_Map startDate={startDate} endDate={endDate} />
        ) : null}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        {alignment === "관능" && secondary === "원육" ? (
          <Sense_Fresh_Corr startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "처리육" ? (
          <Sense_Proc_Corr startDate={startDate} endDate={endDate} />
        ) : alignment === "관능" && secondary === "가열육" ? (
          <Sense_Heated_Corr startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "원육" ? (
          <Taste_Fresh_Corr startDate={startDate} endDate={endDate} />
        ) : alignment === "맛" && secondary === "처리육" ? (
          <Taste_Proc_Corr startDate={startDate} endDate={endDate} />
        ) : null}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={3}>
        <Taste_Time startDate={startDate} endDate={endDate} />
      </CustomTabPanel>
    </Box>
  );
}